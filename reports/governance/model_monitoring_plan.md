# Model Monitoring Plan

## Monitoring objective

Ensure the credit-risk model remains stable, explainable, and operationally useful after deployment or future data refreshes.

## KPI snapshot

| kpi                                      | value                                                                                                              | interpretation                                            |
|:-----------------------------------------|:-------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------|
| Champion model                           | xgboost_weighted                                                                                                   | Selected using validation ranking metrics.                |
| Portfolio default rate                   | 9.04%                                                                                                              | Base rate for interpreting precision and review workload. |
| Recommended objective                    | minimum_cost_review_rate_le_30pct                                                                                  | Threshold-selection business rule.                        |
| Operating threshold                      | 0.565                                                                                                              | Probability cutoff for manual-review flag.                |
| Test ROC-AUC                             | 0.7468                                                                                                             | Out-of-sample ranking performance.                        |
| Test PR-AUC                              | 0.2168                                                                                                             | Ranking performance under class imbalance.                |
| Validation recall at operating threshold | 61.93%                                                                                                             | Defaults captured during threshold selection.             |
| Test recall at operating threshold       | 61.49%                                                                                                             | Out-of-sample defaults captured at selected threshold.    |
| Test precision at operating threshold    | 19.10%                                                                                                             | Share of reviewed accounts that defaulted.                |
| Test review rate at operating threshold  | 29.11%                                                                                                             | Operational workload from the score cutoff.               |
| Test illustrative business cost          | $5,884,500                                                                                                         | Scenario cost using Notebook 07 assumptions.              |
| Top SHAP drivers                         | interest_rate, amount_missing_flag, broad_data_quality_issue_count, total_income_pa, core_data_quality_issue_count | Primary explanation drivers to monitor for drift.         |

## Risk limits and escalation triggers

| metric                                     | baseline                            | warning_limit          | breach_limit           | monitoring_frequency        | action                                                                     |
|:-------------------------------------------|:------------------------------------|:-----------------------|:-----------------------|:----------------------------|:---------------------------------------------------------------------------|
| Population Stability Index - overall score | Training/test score distribution    | > 0.10                 | > 0.25                 | Monthly                     | Investigate portfolio shift, data pipeline changes, and score calibration. |
| Key feature PSI - top SHAP drivers         | Training/test feature distributions | > 0.10                 | > 0.25                 | Monthly                     | Review feature distribution shift and retraining need.                     |
| Operating review rate                      | 29.11%                              | > 34.11%               | > 39.11%               | Weekly/monthly              | Review threshold capacity and manual-review staffing impact.               |
| Recall on matured labels                   | 61.49%                              | < 56.49%               | < 51.49%               | Monthly after labels mature | Assess missed-default concentration and model refresh need.                |
| Precision on reviewed accounts             | 19.10%                              | < 16.10%               | < 14.10%               | Monthly after labels mature | Review false-positive burden and customer-impact risk.                     |
| Critical data-quality missingness          | Notebook 02/03 data-quality profile | +25% relative increase | +50% relative increase | Each data load              | Open data-quality incident and pause model refresh if severe.              |

## Suggested monitoring cadence

- **Each data refresh:** schema checks, duplicate-key checks, missingness checks, and leakage-policy checks.
- **Monthly:** score distribution, review rate, feature drift, data-quality drift, top-SHAP-driver drift.
- **After labels mature:** realized default rate, recall, precision, false negatives, and false positives.
- **Quarterly or material-change event:** threshold review, model challenger review, governance sign-off.

## Escalation actions

If a breach occurs, pause automated refreshes if necessary, document the issue, identify root cause, quantify borrower/business impact, and decide whether remediation, recalibration, threshold adjustment, or retraining is required.
