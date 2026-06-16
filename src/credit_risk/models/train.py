from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

from credit_risk.models.evaluate import (
    evaluate_fitted_model,
    make_prediction_frame,
    model_selection_summary,
)

try:
    from xgboost import XGBClassifier
except Exception:  # pragma: no cover - optional dependency fallback
    XGBClassifier = None


TARGET_COLUMN = "defaulter"
SPLIT_COLUMN = "split"
ID_COLUMNS = ["user_id", "record_sequence"]


@dataclass
class ModelTrainingArtifacts:
    """Container for fitted models and evaluation outputs."""

    fitted_models: dict[str, Pipeline]
    validation_results: pd.DataFrame
    test_results: pd.DataFrame
    selection_summary: pd.DataFrame
    validation_predictions: pd.DataFrame
    test_predictions: pd.DataFrame
    numeric_features: list[str]
    categorical_features: list[str]
    champion_model_name: str


def infer_feature_columns(modeling_df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Infer model feature columns from the leakage-reviewed modelling dataset."""
    excluded = set(ID_COLUMNS + [TARGET_COLUMN, SPLIT_COLUMN])
    feature_cols = [col for col in modeling_df.columns if col not in excluded]
    numeric_features = [col for col in feature_cols if pd.api.types.is_numeric_dtype(modeling_df[col])]
    categorical_features = [col for col in feature_cols if col not in numeric_features]
    return numeric_features, categorical_features


def split_modeling_dataset(
    modeling_df: pd.DataFrame,
    feature_cols: list[str],
) -> dict[str, dict[str, pd.DataFrame | pd.Series]]:
    """Return train, validation, and test frames from the saved split column."""
    required_splits = {"train", "validation", "test"}
    observed_splits = set(modeling_df[SPLIT_COLUMN].dropna().unique())
    missing_splits = required_splits - observed_splits
    if missing_splits:
        raise ValueError(f"Missing required modelling splits: {sorted(missing_splits)}")

    splits: dict[str, dict[str, pd.DataFrame | pd.Series]] = {}
    for split_name in ["train", "validation", "test"]:
        split_df = modeling_df.loc[modeling_df[SPLIT_COLUMN].eq(split_name)].copy()
        splits[split_name] = {
            "X": split_df[feature_cols],
            "y": split_df[TARGET_COLUMN].astype(int),
            "identity": split_df[ID_COLUMNS + [TARGET_COLUMN, SPLIT_COLUMN]].copy(),
        }
    return splits


def build_preprocessor(
    numeric_features: list[str],
    categorical_features: list[str],
    scale_numeric: bool = False,
    categorical_encoding: str = "onehot",
) -> ColumnTransformer:
    """Build a train-only preprocessing step for imputation, scaling, and encoding."""
    numeric_steps: list[tuple[str, Any]] = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))
    numeric_pipeline = Pipeline(numeric_steps)

    if categorical_encoding == "onehot":
        categorical_encoder = OneHotEncoder(
            handle_unknown="ignore",
            min_frequency=50,
            sparse_output=True,
        )
    elif categorical_encoding == "ordinal":
        categorical_encoder = OrdinalEncoder(
            handle_unknown="use_encoded_value",
            unknown_value=-1,
            encoded_missing_value=-1,
        )
    else:
        raise ValueError("categorical_encoding must be 'onehot' or 'ordinal'")

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", categorical_encoder),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
        sparse_threshold=0.30 if categorical_encoding == "onehot" else 0.0,
    )


def default_scale_pos_weight(y_train: pd.Series) -> float:
    """Calculate the non-default to default ratio for weighted XGBoost training."""
    positives = int(y_train.sum())
    negatives = int(len(y_train) - positives)
    if positives == 0:
        return 1.0
    return negatives / positives


def build_candidate_models(
    numeric_features: list[str],
    categorical_features: list[str],
    y_train: pd.Series,
    random_state: int = 42,
) -> dict[str, Pipeline]:
    """Build candidate models aligned to credit-risk modelling requirements."""
    models: dict[str, Pipeline] = {}

    models["logistic_regression_balanced"] = Pipeline(
        steps=[
            (
                "preprocess",
                build_preprocessor(
                    numeric_features,
                    categorical_features,
                    scale_numeric=True,
                    categorical_encoding="onehot",
                ),
            ),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=300,
                    solver="liblinear",
                    random_state=random_state,
                ),
            ),
        ]
    )

    models["random_forest_balanced"] = Pipeline(
        steps=[
            (
                "preprocess",
                build_preprocessor(
                    numeric_features,
                    categorical_features,
                    scale_numeric=False,
                    categorical_encoding="ordinal",
                ),
            ),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=150,
                    max_depth=12,
                    min_samples_leaf=100,
                    max_features="sqrt",
                    class_weight="balanced_subsample",
                    n_jobs=-1,
                    random_state=random_state,
                ),
            ),
        ]
    )

    if XGBClassifier is not None:
        models["xgboost_weighted"] = Pipeline(
            steps=[
                (
                    "preprocess",
                    build_preprocessor(
                        numeric_features,
                        categorical_features,
                        scale_numeric=False,
                        categorical_encoding="ordinal",
                    ),
                ),
                (
                    "model",
                    XGBClassifier(
                        n_estimators=200,
                        max_depth=4,
                        learning_rate=0.06,
                        subsample=0.85,
                        colsample_bytree=0.85,
                        reg_lambda=2.0,
                        objective="binary:logistic",
                        eval_metric="logloss",
                        tree_method="hist",
                        scale_pos_weight=default_scale_pos_weight(y_train),
                        n_jobs=1,
                        random_state=random_state,
                    ),
                ),
            ]
        )

    return models


def train_and_evaluate_candidate_models(
    modeling_df: pd.DataFrame,
    random_state: int = 42,
) -> ModelTrainingArtifacts:
    """Fit candidate models and evaluate them on validation and test splits."""
    numeric_features, categorical_features = infer_feature_columns(modeling_df)
    feature_cols = numeric_features + categorical_features
    splits = split_modeling_dataset(modeling_df, feature_cols)

    X_train = splits["train"]["X"]
    y_train = splits["train"]["y"]
    X_validation = splits["validation"]["X"]
    y_validation = splits["validation"]["y"]
    X_test = splits["test"]["X"]
    y_test = splits["test"]["y"]

    candidate_models = build_candidate_models(
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        y_train=y_train,
        random_state=random_state,
    )

    fitted_models: dict[str, Pipeline] = {}
    validation_metric_rows: list[dict[str, Any]] = []
    test_metric_rows: list[dict[str, Any]] = []
    validation_prediction_frames: list[pd.DataFrame] = []
    test_prediction_frames: list[pd.DataFrame] = []

    for model_name, pipeline in candidate_models.items():
        pipeline.fit(X_train, y_train)
        fitted_models[model_name] = pipeline

        validation_metric_rows.append(
            evaluate_fitted_model(model_name, pipeline, X_validation, y_validation, dataset_name="validation")
        )
        test_metric_rows.append(
            evaluate_fitted_model(model_name, pipeline, X_test, y_test, dataset_name="test")
        )

        validation_prediction_frames.append(
            make_prediction_frame(
                model_name,
                pipeline,
                X_validation,
                splits["validation"]["identity"],
            )
        )
        test_prediction_frames.append(
            make_prediction_frame(
                model_name,
                pipeline,
                X_test,
                splits["test"]["identity"],
            )
        )

    validation_results = pd.DataFrame(validation_metric_rows).sort_values("pr_auc", ascending=False).reset_index(drop=True)
    test_results = pd.DataFrame(test_metric_rows).sort_values("pr_auc", ascending=False).reset_index(drop=True)
    selection = model_selection_summary(validation_results)
    champion_model_name = str(selection.iloc[0]["model_name"])

    return ModelTrainingArtifacts(
        fitted_models=fitted_models,
        validation_results=validation_results,
        test_results=test_results,
        selection_summary=selection,
        validation_predictions=pd.concat(validation_prediction_frames, ignore_index=True),
        test_predictions=pd.concat(test_prediction_frames, ignore_index=True),
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        champion_model_name=champion_model_name,
    )


def save_model_training_artifacts(
    artifacts: ModelTrainingArtifacts,
    table_dir: Path,
    model_artifact_dir: Path,
) -> None:
    """Persist fitted models, metrics, and prediction outputs."""
    table_dir.mkdir(parents=True, exist_ok=True)
    model_artifact_dir.mkdir(parents=True, exist_ok=True)

    artifacts.validation_results.to_csv(table_dir / "model_validation_results_default_threshold.csv", index=False)
    artifacts.test_results.to_csv(table_dir / "model_test_results_default_threshold.csv", index=False)
    artifacts.selection_summary.to_csv(table_dir / "model_selection_summary.csv", index=False)
    artifacts.validation_predictions.to_csv(table_dir / "validation_predictions_default_threshold.csv", index=False)
    artifacts.test_predictions.to_csv(table_dir / "test_predictions_default_threshold.csv", index=False)

    joblib.dump(artifacts.fitted_models, model_artifact_dir / "candidate_models.joblib")
    joblib.dump(
        artifacts.fitted_models[artifacts.champion_model_name],
        model_artifact_dir / "champion_model.joblib",
    )

    feature_metadata = {
        "numeric_features": artifacts.numeric_features,
        "categorical_features": artifacts.categorical_features,
        "champion_model_name": artifacts.champion_model_name,
    }
    joblib.dump(feature_metadata, model_artifact_dir / "model_feature_metadata.joblib")
