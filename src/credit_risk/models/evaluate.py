from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)


DEFAULT_FALSE_NEGATIVE_COST = 5_000
DEFAULT_FALSE_POSITIVE_COST = 500


def predict_default_probability(model, X: pd.DataFrame) -> np.ndarray:
    """Return positive-class default probabilities for a fitted classifier."""
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        return np.asarray(proba)[:, 1]
    if hasattr(model, "decision_function"):
        scores = np.asarray(model.decision_function(X))
        return 1 / (1 + np.exp(-scores))
    raise TypeError("Model must expose predict_proba or decision_function.")


def classification_metrics_at_threshold(
    y_true: Iterable[int],
    y_score: Iterable[float],
    threshold: float = 0.50,
    false_negative_cost: float = DEFAULT_FALSE_NEGATIVE_COST,
    false_positive_cost: float = DEFAULT_FALSE_POSITIVE_COST,
) -> dict[str, float]:
    """Calculate ranking, classification, calibration, and simple business-cost metrics."""
    y_true_arr = np.asarray(y_true).astype(int)
    y_score_arr = np.asarray(y_score).astype(float)
    y_pred = (y_score_arr >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true_arr, y_pred, labels=[0, 1]).ravel()
    business_cost = fn * false_negative_cost + fp * false_positive_cost

    return {
        "threshold": float(threshold),
        "roc_auc": float(roc_auc_score(y_true_arr, y_score_arr)),
        "pr_auc": float(average_precision_score(y_true_arr, y_score_arr)),
        "brier_score": float(brier_score_loss(y_true_arr, y_score_arr)),
        "accuracy": float(accuracy_score(y_true_arr, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true_arr, y_pred)),
        "precision": float(precision_score(y_true_arr, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true_arr, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true_arr, y_pred, zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true_arr, y_pred)),
        "review_rate": float(y_pred.mean()),
        "business_cost": float(business_cost),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
        "default_count": int(y_true_arr.sum()),
        "non_default_count": int((1 - y_true_arr).sum()),
    }


def evaluate_fitted_model(
    model_name: str,
    model,
    X: pd.DataFrame,
    y: pd.Series,
    dataset_name: str,
    threshold: float = 0.50,
    false_negative_cost: float = DEFAULT_FALSE_NEGATIVE_COST,
    false_positive_cost: float = DEFAULT_FALSE_POSITIVE_COST,
) -> dict[str, float | str]:
    """Evaluate a fitted model and return one row of metrics."""
    y_score = predict_default_probability(model, X)
    metrics = classification_metrics_at_threshold(
        y,
        y_score,
        threshold=threshold,
        false_negative_cost=false_negative_cost,
        false_positive_cost=false_positive_cost,
    )
    return {
        "model_name": model_name,
        "dataset": dataset_name,
        **metrics,
    }


def make_prediction_frame(
    model_name: str,
    model,
    features: pd.DataFrame,
    identity_frame: pd.DataFrame,
    threshold: float = 0.50,
) -> pd.DataFrame:
    """Create an auditable prediction frame with IDs, target, split, and probabilities."""
    scores = predict_default_probability(model, features)
    output = identity_frame.copy()
    output["model_name"] = model_name
    output["predicted_default_probability"] = scores
    output["predicted_label_at_0_50"] = (scores >= threshold).astype(int)
    return output


def model_selection_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Rank validation results using credit-risk oriented model-selection criteria."""
    sort_cols = ["pr_auc", "roc_auc", "balanced_accuracy", "mcc"]
    ascending = [False, False, False, False]
    return (
        results.sort_values(sort_cols, ascending=ascending)
        .assign(selection_rank=lambda x: range(1, len(x) + 1))
        [[
            "selection_rank",
            "model_name",
            "dataset",
            "pr_auc",
            "roc_auc",
            "brier_score",
            "recall",
            "precision",
            "f1",
            "balanced_accuracy",
            "mcc",
            "review_rate",
            "business_cost",
            "false_negative",
            "false_positive",
            "true_positive",
            "true_negative",
        ]]
    )
