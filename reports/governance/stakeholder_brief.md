# Stakeholder Brief - Retail Credit Default-Risk Model

## What the model does

The model ranks borrowers by estimated default risk so that a credit-risk team can prioritize manual review and portfolio monitoring.

## Recommended operating point

- **Champion model:** xgboost_weighted
- **Operating threshold:** 0.565
- **Test recall:** 61.49%
- **Test precision:** 19.10%
- **Test review rate:** 29.11%

## Business interpretation

At the selected threshold, the model captures a meaningful share of future defaults while keeping the review population below the operational cap used in this project. This makes it more practical than using the default 0.50 cutoff.

## Main risk drivers identified by explainability

| raw_feature                    | feature_label                  |   mean_abs_shap |   mean_shap |   transformed_feature_count | governance_note                                                                             |
|:-------------------------------|:-------------------------------|----------------:|------------:|----------------------------:|:--------------------------------------------------------------------------------------------|
| interest_rate                  | Interest Rate                  |       0.618882  |  -0.0548024 |                           1 | Pricing/risk signal: explain carefully because pricing can reflect prior underwriting risk. |
| amount_missing_flag            | Amount Missing Flag            |       0.358383  |   0.0803676 |                           1 | Data-quality signal: monitor for drift and do not interpret as borrower behaviour alone.    |
| broad_data_quality_issue_count | Broad Data Quality Issue Count |       0.170565  |  -0.0501884 |                           1 | Data-quality signal: monitor for drift and do not interpret as borrower behaviour alone.    |
| total_income_pa                | Total Income Pa                |       0.138081  |  -0.0192555 |                           1 | Affordability/exposure signal: suitable for portfolio-risk interpretation.                  |
| core_data_quality_issue_count  | Core Data Quality Issue Count  |       0.0856402 |  -0.0659113 |                           1 | Data-quality signal: monitor for drift and do not interpret as borrower behaviour alone.    |

## How this should be used

Use the score to support analyst review, portfolio segmentation, and monitoring. Do not use it as a standalone automated lending decision without additional validation, fairness testing, compliance review, and production monitoring.
