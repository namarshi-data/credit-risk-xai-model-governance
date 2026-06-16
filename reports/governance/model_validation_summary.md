# Model Validation Summary

## Executive summary

This project develops a leakage-reviewed, explainable default-risk model for a Canadian retail credit portfolio. The model is positioned as a **manual-review prioritization and portfolio-monitoring tool**, not as an automated decline engine.

| champion_model   |   modeling_rows |   portfolio_default_rate |   operating_threshold | threshold_objective               |   test_recall |   test_precision |   test_review_rate |   test_business_cost | primary_governance_decision                                                                            |
|:-----------------|----------------:|-------------------------:|----------------------:|:----------------------------------|--------------:|-----------------:|-------------------:|---------------------:|:-------------------------------------------------------------------------------------------------------|
| xgboost_weighted |          134417 |                0.0904127 |                 0.565 | minimum_cost_review_rate_le_30pct |       0.61492 |         0.190971 |           0.291127 |           5.8845e+06 | Use as decision-support/manual-review prioritization model, not as an automated credit-decline engine. |

## Performance evidence

| evaluation_view                         | model_name       | dataset    |   threshold |   roc_auc |   pr_auc |   brier_score |   recall |   precision |       f1 |   balanced_accuracy |      mcc |   review_rate |   business_cost |   false_negative |   false_positive |   true_positive |   true_negative | selected_operating_threshold   |
|:----------------------------------------|:-----------------|:-----------|------------:|----------:|---------:|--------------:|---------:|------------:|---------:|--------------------:|---------:|--------------:|----------------:|-----------------:|-----------------:|----------------:|----------------:|:-------------------------------|
| validation_default_0_50                 | xgboost_weighted | validation |       0.5   |  0.751101 | 0.229393 |      0.204092 | 0.72079  |    0.171429 | 0.276981 |            0.687249 | 0.221241 |      0.380152 |      5.7205e+06 |              509 |             6351 |            1314 |           11989 | False                          |
| test_default_0_50                       | xgboost_weighted | test       |       0.5   |  0.746768 | 0.216785 |      0.203494 | 0.727372 |    0.172904 | 0.279393 |            0.690758 | 0.225365 |      0.38035  |      5.6565e+06 |              497 |             6343 |            1326 |           11997 | False                          |
| validation_selected_operating_threshold | xgboost_weighted | validation |       0.565 |  0.751101 | 0.229393 |      0.204092 | 0.619309 |    0.18962  | 0.290343 |            0.678111 | 0.223938 |      0.295293 |      5.8825e+06 |              694 |             4825 |            1129 |           13515 | True                           |
| test_selected_operating_threshold       | xgboost_weighted | test       |       0.565 |  0.746768 | 0.216785 |      0.203494 | 0.61492  |    0.190971 | 0.291434 |            0.677989 | 0.224717 |      0.291127 |      5.8845e+06 |              702 |             4749 |            1121 |           13591 | True                           |

## Feature governance

|   feature_count |
|----------------:|
|              64 |

## Control register

| control_area            | risk                                                                           | control                                                                                                                 | evidence                                                           | owner                                 | frequency                                    |
|:------------------------|:-------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------|:--------------------------------------|:---------------------------------------------|
| Data ingestion          | Many-to-many sheet merge inflates borrower records and changes target rate.    | Merge sheets using user_id plus record_sequence and test duplicate record keys.                                         | Notebook 01 ingestion summary and record-key duplicate check.      | Risk analytics                        | Each data refresh                            |
| Data quality            | Missing amount/employment fields may distort score interpretation.             | Create missingness flags, monitor missingness rates, and retain data-quality features only where justified.             | Notebook 02/03 missingness and data-quality flag summaries.        | Data analyst / data steward           | Monthly                                      |
| Leakage prevention      | Repayment-derived variables can leak target information into model training.   | Exclude total_payment, received_principal, interest_received, and derived repayment ratios from model features.         | Feature leakage and usage policy table.                            | Model developer                       | Before each model release                    |
| Fairness and proxy risk | Sensitive/proxy variables could create unfair or hard-to-defend decisions.     | Exclude gender, marital status, pincode, and social profile from baseline model; retain only for approved audit review. | Feature policy and model feature catalogue.                        | Model governance / compliance partner | Before release and annually                  |
| Model performance       | Model ranking weakens or becomes unstable after deployment.                    | Monitor PR-AUC, ROC-AUC, recall, precision, Brier score, and confusion-matrix outcomes when labels mature.              | Notebook 06 validation/test results.                               | Model monitoring team                 | Monthly/quarterly                            |
| Threshold governance    | Operating threshold overloads manual review teams or misses too many defaults. | Select threshold on validation data using business-cost and review-cap constraints; validate once on test data.         | Notebook 07 threshold shortlist and recommended threshold summary. | Credit-risk strategy                  | Quarterly or after material portfolio change |
| Explainability          | Stakeholders cannot understand why accounts are sent to review.                | Provide global SHAP drivers, local reason codes, anchor-like rules, and counterfactual scenario diagnostics.            | Notebook 08 XAI outputs.                                           | Risk analytics / model validation     | Each model release                           |
| Ongoing monitoring      | Population, score, or data-quality drift changes model behaviour.              | Track score distribution, review rate, feature missingness, top-driver PSI, and realized default outcomes.              | Notebook 09 monitoring plan and risk-limit register.               | Model owner                           | Monthly                                      |

## Validation decision

The model is acceptable for portfolio analytics and decision-support demonstration purposes, subject to the monitoring plan and the limitations documented here. Before production use, the model would require independent validation, data lineage review, calibration review, fairness testing, privacy/legal review, and user-acceptance testing with credit-risk stakeholders.
