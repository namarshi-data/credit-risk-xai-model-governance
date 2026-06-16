# Model Card - Canadian Retail Credit Risk XAI

## Model overview

- **Business purpose:** Early-warning retail credit default-risk ranking and manual-review prioritization.
- **Champion model:** `xgboost_weighted`
- **Operating threshold:** `0.565`
- **Threshold objective:** `minimum_cost_review_rate_le_30pct`
- **Target:** borrower default indicator.
- **Intended use:** decision support for portfolio monitoring and risk review.
- **Out-of-scope use:** automated credit decline, pricing decisioning, or adverse-action communication without additional validation, legal review, and fairness assessment.

## Model inventory

| item                   | value                                                                                   |
|:-----------------------|:----------------------------------------------------------------------------------------|
| business_use           | Early-warning retail credit default-risk ranking and manual-review prioritization       |
| target                 | Defaulter indicator                                                                     |
| champion_model         | xgboost_weighted                                                                        |
| operating_threshold    | 0.565                                                                                   |
| threshold_objective    | minimum_cost_review_rate_le_30pct                                                       |
| modeling_rows          | 134417                                                                                  |
| portfolio_default_rate | 0.0904126710163149                                                                      |
| model_feature_count    | 47                                                                                      |
| sensitive_proxy_use    | Excluded from baseline model; retained only for audit/governance review where permitted |
| leakage_control        | Repayment-derived variables excluded from model features                                |

## Validation and test performance

| evaluation_view                         | model_name       | dataset    |   threshold |   roc_auc |   pr_auc |   brier_score |   recall |   precision |       f1 |   balanced_accuracy |      mcc |   review_rate |   business_cost |   false_negative |   false_positive |   true_positive |   true_negative | selected_operating_threshold   |
|:----------------------------------------|:-----------------|:-----------|------------:|----------:|---------:|--------------:|---------:|------------:|---------:|--------------------:|---------:|--------------:|----------------:|-----------------:|-----------------:|----------------:|----------------:|:-------------------------------|
| validation_default_0_50                 | xgboost_weighted | validation |       0.5   |  0.751101 | 0.229393 |      0.204092 | 0.72079  |    0.171429 | 0.276981 |            0.687249 | 0.221241 |      0.380152 |      5.7205e+06 |              509 |             6351 |            1314 |           11989 | False                          |
| test_default_0_50                       | xgboost_weighted | test       |       0.5   |  0.746768 | 0.216785 |      0.203494 | 0.727372 |    0.172904 | 0.279393 |            0.690758 | 0.225365 |      0.38035  |      5.6565e+06 |              497 |             6343 |            1326 |           11997 | False                          |
| validation_selected_operating_threshold | xgboost_weighted | validation |       0.565 |  0.751101 | 0.229393 |      0.204092 | 0.619309 |    0.18962  | 0.290343 |            0.678111 | 0.223938 |      0.295293 |      5.8825e+06 |              694 |             4825 |            1129 |           13515 | True                           |
| test_selected_operating_threshold       | xgboost_weighted | test       |       0.565 |  0.746768 | 0.216785 |      0.203494 | 0.61492  |    0.190971 | 0.291434 |            0.677989 | 0.224717 |      0.291127 |      5.8845e+06 |              702 |             4749 |            1121 |           13591 | True                           |

## Top explainability drivers

| raw_feature                    | feature_label                  |   mean_abs_shap |    mean_shap |   transformed_feature_count | governance_note                                                                             |
|:-------------------------------|:-------------------------------|----------------:|-------------:|----------------------------:|:--------------------------------------------------------------------------------------------|
| interest_rate                  | Interest Rate                  |       0.618882  | -0.0548024   |                           1 | Pricing/risk signal: explain carefully because pricing can reflect prior underwriting risk. |
| amount_missing_flag            | Amount Missing Flag            |       0.358383  |  0.0803676   |                           1 | Data-quality signal: monitor for drift and do not interpret as borrower behaviour alone.    |
| broad_data_quality_issue_count | Broad Data Quality Issue Count |       0.170565  | -0.0501884   |                           1 | Data-quality signal: monitor for drift and do not interpret as borrower behaviour alone.    |
| total_income_pa                | Total Income Pa                |       0.138081  | -0.0192555   |                           1 | Affordability/exposure signal: suitable for portfolio-risk interpretation.                  |
| core_data_quality_issue_count  | Core Data Quality Issue Count  |       0.0856402 | -0.0659113   |                           1 | Data-quality signal: monitor for drift and do not interpret as borrower behaviour alone.    |
| loan_to_income_band            | Loan To Income Band            |       0.07313   |  0.0236194   |                           1 | Affordability/exposure signal: suitable for portfolio-risk interpretation.                  |
| high_interest_flag             | High Interest Flag             |       0.0720735 |  0.014624    |                           1 | Pricing/risk signal: explain carefully because pricing can reflect prior underwriting risk. |
| tenure_years                   | Tenure Years                   |       0.0599833 | -0.0113899   |                           1 | Segment/product signal: monitor segment stability and business reasonableness.              |
| loan_category                  | Loan Category                  |       0.0533629 |  0.000128962 |                           1 | Segment/product signal: monitor segment stability and business reasonableness.              |
| amount                         | Amount                         |       0.0435313 | -0.0164518   |                           1 | Affordability/exposure signal: suitable for portfolio-risk interpretation.                  |

## Key controls

- Repayment-derived variables are excluded from the modelling feature set to reduce target leakage risk.
- Sensitive/proxy-sensitive attributes are excluded from the baseline model and retained only for permitted audit/governance review.
- The operating threshold is selected on validation data and reviewed once on the held-out test split.
- Counterfactual scenarios are diagnostic only and should not be interpreted as customer instructions.

## Monitoring limits

| metric                                     | baseline                            | warning_limit          | breach_limit           | monitoring_frequency        | action                                                                     |
|:-------------------------------------------|:------------------------------------|:-----------------------|:-----------------------|:----------------------------|:---------------------------------------------------------------------------|
| Population Stability Index - overall score | Training/test score distribution    | > 0.10                 | > 0.25                 | Monthly                     | Investigate portfolio shift, data pipeline changes, and score calibration. |
| Key feature PSI - top SHAP drivers         | Training/test feature distributions | > 0.10                 | > 0.25                 | Monthly                     | Review feature distribution shift and retraining need.                     |
| Operating review rate                      | 29.11%                              | > 34.11%               | > 39.11%               | Weekly/monthly              | Review threshold capacity and manual-review staffing impact.               |
| Recall on matured labels                   | 61.49%                              | < 56.49%               | < 51.49%               | Monthly after labels mature | Assess missed-default concentration and model refresh need.                |
| Precision on reviewed accounts             | 19.10%                              | < 16.10%               | < 14.10%               | Monthly after labels mature | Review false-positive burden and customer-impact risk.                     |
| Critical data-quality missingness          | Notebook 02/03 data-quality profile | +25% relative increase | +50% relative increase | Each data load              | Open data-quality incident and pause model refresh if severe.              |
