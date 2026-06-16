# Interview Talking Points

## 30-second project pitch

I built an end-to-end Canadian retail credit risk analytics project that predicts borrower default risk and supports portfolio monitoring, explainability, and model governance. The project starts with multi-sheet Excel ingestion and data-quality review, then builds leakage-controlled features, trains logistic regression, random forest, and XGBoost models, selects a business operating threshold under a manual-review cap, and produces SHAP explanations, counterfactual diagnostics, a model card, validation summary, control register, and monitoring plan.

## 60-second project pitch

This project simulates how a Canadian retail lender could prioritize borrowers for credit-risk review. I started by validating the data grain across multiple Excel sheets because a naïve merge created inflated row counts. After fixing the merge logic, I performed data quality checks, created missingness flags, and identified that missing loan amount information was both a data-quality issue and a risk signal. I then performed portfolio monitoring by loan category, employment type, interest-rate band, income, and loan-to-income profile.

For modelling, I excluded leakage-prone repayment variables and sensitive/proxy-sensitive fields from the baseline model. I trained logistic regression, random forest, and XGBoost models, and selected XGBoost as the champion. Instead of relying on the default 0.50 cutoff, I selected an operating threshold of 0.565 based on validation performance, business cost, and review-cap constraints. On the test set, the model captured about 61% of defaults with a 29% review rate. I finished the project with SHAP explainability, local explanations, counterfactual diagnostics, and governance documents including a model card, validation summary, risk limits, and monitoring plan.

## Questions and answers

### Why did you frame this as early-warning risk review instead of automated credit approval?

Because the dataset includes behavioural and portfolio-level information, and because credit-risk models in financial institutions require strong validation, fairness review, governance, and policy approval before they can be used for automated decisions. Positioning the model as a review-prioritization tool is more realistic and safer.

### What was the most important data issue you found?

The first major issue was record-grain integrity. Each source sheet had duplicate user IDs, so merging only on user ID created a many-to-many merge and inflated the row count. I fixed this by creating a record sequence per user and merging on user ID plus record sequence. That preserved the correct row count and protected downstream portfolio KPIs and model metrics.

### How did you handle class imbalance?

The default rate was about 9%, so accuracy was not the primary metric. I used class-weighted models and evaluated PR-AUC, ROC-AUC, recall, precision, F1, MCC, balanced accuracy, review rate, and business cost. I also selected the final threshold using validation data rather than defaulting to 0.50.

### Why did you exclude repayment-derived variables?

Repayment-derived variables may contain information that occurs after or near the default outcome, which can create target leakage. I kept those variables for monitoring analysis but excluded them from the predictive model feature set.

### Why did you keep missingness flags?

Missingness was not random. For example, missing loan amount information showed a higher observed default rate, so I treated missingness as a potential operational risk signal. I created missingness flags instead of dropping incomplete records.

### Why was XGBoost selected as the champion model?

XGBoost had the strongest validation performance overall, especially on PR-AUC and ROC-AUC, while maintaining stable test performance. It also worked well with SHAP for explainability, which was important for stakeholder and governance communication.

### Why did you not optimize for 95% accuracy?

In an imbalanced default dataset, high accuracy can be misleading because a model could predict most borrowers as non-default and still appear accurate. I focused on recall, precision, PR-AUC, review rate, and cost because those are more relevant to credit-risk operations.

### What does the selected threshold mean?

The selected threshold of 0.565 is the probability cutoff used to send borrowers to manual review. It was chosen because it balanced default capture and operational workload. On the test set, it captured about 61% of defaults while reviewing about 29% of borrowers.

### How did you explain the model?

I used global SHAP importance to identify portfolio-level drivers, dependence-style plots to understand feature effects, local explanations for individual borrower scores, anchor-like rules for business-readable patterns, and counterfactual diagnostics to understand model sensitivity.

### What are the main governance controls?

The project documents data-grain validation, data-quality controls, leakage prevention, sensitive/proxy-feature exclusion, validation-based threshold selection, held-out test evaluation, explainability review, model risk limits, and monitoring KPIs.

### How would you improve this project in a real bank?

I would add time-based validation, monthly performance monitoring, champion/challenger tracking, fairness testing, reject inference if applicable, policy-aligned adverse-action reason codes, independent model validation, and integration with SQL/Power BI dashboards for portfolio monitoring.

## Resume bullets

- Built an end-to-end retail credit risk analytics pipeline in Python covering data ingestion, data-quality profiling, portfolio monitoring, feature engineering, model training, threshold selection, explainability, and governance documentation.
- Trained and evaluated logistic regression, random forest, and XGBoost default-risk models on 134K borrower records using PR-AUC, ROC-AUC, recall, precision, MCC, review rate, and illustrative business-cost metrics.
- Selected a validation-based operating threshold that captured 61.49% of defaults on the test set while limiting the manual-review population to 29.11%.
- Implemented leakage controls by excluding repayment-derived variables from modelling and retaining sensitive/proxy-sensitive fields only for governance review.
- Produced SHAP explainability, local borrower-level explanations, counterfactual diagnostics, model card, validation summary, control register, and monitoring plan.
