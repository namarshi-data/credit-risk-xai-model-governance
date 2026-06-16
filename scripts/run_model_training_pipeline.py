from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from credit_risk.config import MODEL_ARTIFACT_DIR, PROCESSED_DIR, TABLE_DIR, ensure_project_directories
from credit_risk.models.train import save_model_training_artifacts, train_and_evaluate_candidate_models


def main() -> None:
    ensure_project_directories()

    input_path = PROCESSED_DIR / "credit_risk_modeling_dataset.csv"
    if not input_path.exists():
        raise FileNotFoundError(
            f"Missing modelling dataset: {input_path}. Run scripts/run_feature_engineering_pipeline.py first."
        )

    modeling_df = pd.read_csv(input_path, low_memory=False)
    required_cols = {"user_id", "record_sequence", "defaulter", "split"}
    missing_cols = required_cols - set(modeling_df.columns)
    if missing_cols:
        raise ValueError(f"The modelling dataset is missing required columns: {sorted(missing_cols)}")

    artifacts = train_and_evaluate_candidate_models(modeling_df, random_state=42)
    save_model_training_artifacts(artifacts, TABLE_DIR, MODEL_ARTIFACT_DIR)

    print("Model training completed")
    print(f"Input shape: {modeling_df.shape}")
    print(f"Numeric features: {len(artifacts.numeric_features)}")
    print(f"Categorical features: {len(artifacts.categorical_features)}")
    print(f"Champion model: {artifacts.champion_model_name}")
    print("Validation results at default 0.50 threshold:")
    display_cols = [
        "model_name",
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
    ]
    print(artifacts.validation_results[display_cols].to_string(index=False))


if __name__ == "__main__":
    main()
