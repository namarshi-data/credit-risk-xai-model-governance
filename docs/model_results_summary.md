# Model Results Summary

## Purpose

This document summarizes the model-development results for the Retail Credit Risk Analytics project. The model is designed to rank borrowers by default risk for manual-review prioritization and portfolio monitoring. It is not intended for automated credit approval, automated credit decline, or customer-facing decisioning.

## Portfolio and Target Overview

| Item | Result |
|---|---:|
| Portfolio records | 134,417 |
| Observed default rate | 9.04% |
| Total portfolio exposure | ~$14.70B |
| Defaulted exposure share | 5.96% |
| Modelling objective | Default-risk ranking |
| Primary operating use | Manual-review prioritization |

## Models Evaluated

The project compares baseline and challenger models suitable for imbalanced credit-risk classification:

| Model | Role in project |
|---|---|
| Logistic Regression baseline | Interpretable benchmark model |
| Random Forest weighted baseline | Non-linear tree-based baseline |
| Random Forest tuned challenger | Tuned non-linear challenger |
| XGBoost weighted baseline | Final champion operating model |
| XGBoost tuned challenger | Tuned challenger model |
| Train-only resampling challengers | Optional imbalance-handling experiments |

## Evaluation Metrics

Accuracy is not used as the main performance measure because default prediction is an imbalanced classification problem. The project uses metrics that better represent risk-ranking performance and operational trade-offs.

| Metric | Why it matters |
|---|---|
| ROC-AUC | Measures ranking quality across thresholds |
| PR-AUC | More informative when defaults are a minority class |
| Recall | Measures share of observed defaults captured |
| Precision | Measures quality of reviewed borrower population |
| Review rate | Measures operational workload created by the threshold |
| F1 score | Balances precision and recall |
| Brier score | Supports probability-quality review |
| Business cost | Illustrative threshold-comparison measure |

## Champion Model

| Item | Result |
|---|---:|
| Champion operating model | XGBoost weighted baseline |
| Validation ROC-AUC | 0.7512 |
| Validation PR-AUC | 0.2263 |
| Test ROC-AUC | 0.7478 |
| Test PR-AUC | 0.2147 |
| Selected operating threshold | 0.560 |
| Test recall at selected threshold | 62.21% |
| Test precision at selected threshold | 19.09% |
| Test review rate at selected threshold | 29.46% |

## Threshold Comparison

### Default 0.50 Threshold

| Dataset | ROC-AUC | PR-AUC | Recall | Precision | Review rate |
|---|---:|---:|---:|---:|---:|
| Validation | 0.7512 | 0.2263 | 71.59% | 17.09% | 37.76% |
| Test | 0.7478 | 0.2147 | 71.56% | 17.18% | 37.69% |

### Selected Operating Threshold: 0.560

| Dataset | Recall | Precision | Review rate | Business cost | Business interpretation |
|---|---:|---:|---:|---:|---|
| Validation | 62.59% | 19.05% | 29.71% | $5.83M | Selected under review-cap constraint |
| Test | 62.21% | 19.09% | 29.46% | $5.85M | Held-out confirmation of selected policy |

## Business Interpretation

The selected threshold reduces the review population from roughly 38% at the default 0.50 cutoff to below the 30% review-cap assumption, while still capturing approximately 62% of observed defaults in the held-out test set.

This makes the model more operationally usable because it converts default-risk scores into a review-prioritization process:

1. Rank borrowers by predicted default risk.
2. Review the highest-risk accounts first.
3. Monitor risk concentration and model performance over time.
4. Use explanations and governance controls before taking business action.

## Why the Result Is Credible

The final result is intentionally moderate rather than near-perfect. In credit risk modelling, extremely high performance can indicate target leakage, post-outcome variables, or evaluation on contaminated data.

Credibility controls used in the project include:

- Leakage-safe feature selection
- Train, validation, and test separation
- Threshold selection on validation data only
- Final confirmation on untouched test data
- Review-rate constraint for operational realism
- PR-AUC and recall/precision trade-off analysis
- Responsible-use limitation to manual-review prioritization

## Limitation

Business-cost values are illustrative scenario assumptions for threshold comparison. They are not accounting estimates, IFRS 9 expected-credit-loss estimates, regulatory capital estimates, or production loss forecasts.
