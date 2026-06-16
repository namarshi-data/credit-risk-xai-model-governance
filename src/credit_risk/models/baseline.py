"""Baseline model helpers.

Notebook 06 intentionally keeps the baseline simple and auditable: a class-weighted
logistic regression benchmark, a class-weighted random forest, and a weighted XGBoost
candidate. Hyperparameter optimization is introduced later only after the modelling
pipeline and validation logic are stable.
"""

from credit_risk.models.train import build_candidate_models, build_preprocessor

__all__ = ["build_candidate_models", "build_preprocessor"]
