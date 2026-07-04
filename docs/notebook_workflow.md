# Notebook Workflow

## Purpose

This document explains the notebook sequence used in the Retail Credit Risk Analytics project. The notebooks are designed to move from business framing and data-quality review through modelling, explainability, threshold selection, and governance documentation.

## Notebook Sequence

| Notebook | Purpose | Main output |
|---|---|---|
| `00_project_brief_and_business_context.ipynb` | Defines the business context, scope, stakeholder use case, and responsible-use boundaries | Project scope and intended-use statement |
| `01_data_ingestion_and_schema_review.ipynb` | Reviews Excel workbook sheets, validates record grain, and documents merge logic | Schema summary and ingestion checks |
| `02_data_quality_assessment.ipynb` | Assesses missingness, duplicates, invalid values, logical issues, and leakage risks | Data-quality findings and issue log |
| `03_data_cleaning_and_preprocessing.ipynb` | Cleans data, creates missingness flags, standardizes fields, and generates audit outputs | Cleaned modelling-ready dataset |
| `04_credit_risk_eda_and_portfolio_monitoring.ipynb` | Performs portfolio monitoring, exposure analysis, segment risk review, and EDA | Portfolio risk insights and monitoring tables |
| `05_feature_engineering_and_leakage_review.ipynb` | Engineers features, defines leakage-safe modelling policy, and prepares train/validation/test splits | Feature set and modelling splits |
| `06_model_training_and_evaluation.ipynb` | Trains and compares Logistic Regression, Random Forest, and XGBoost models | Model comparison and validation results |
| `07_threshold_selection_and_business_costing.ipynb` | Selects operating threshold using validation data, review-cap limits, and cost assumptions | Selected threshold and test confirmation |
| `08_explainable_ai_shap_anchors_counterfactuals.ipynb` | Produces SHAP explanations, local explanations, anchor-style rules, and counterfactual diagnostics | Explainability artifacts and stakeholder interpretation tables |
| `09_model_governance_and_monitoring.ipynb` | Creates model card, validation summary, monitoring plan, control register, and stakeholder brief | Governance documentation and monitoring outputs |

## Workflow Logic

```text
Raw Excel workbook
        ↓
Business context and responsible-use scope
        ↓
Data ingestion and schema review
        ↓
Data quality assessment
        ↓
Cleaning and preprocessing
        ↓
Portfolio monitoring and EDA
        ↓
Feature engineering and leakage review
        ↓
Model training and validation
        ↓
Threshold selection and business costing
        ↓
Explainable AI outputs
        ↓
Model governance and monitoring documentation
```

## Suggested Review Order

For recruiters or hiring managers, the fastest review path is:

1. `00_project_brief_and_business_context.ipynb`
2. `04_credit_risk_eda_and_portfolio_monitoring.ipynb`
3. `06_model_training_and_evaluation.ipynb`
4. `07_threshold_selection_and_business_costing.ipynb`
5. `08_explainable_ai_shap_anchors_counterfactuals.ipynb`
6. `09_model_governance_and_monitoring.ipynb`

For technical review, run the notebooks from `00` to `09` in order.

## Key Analyst Skills Demonstrated

| Workflow stage | Skills demonstrated |
|---|---|
| Business framing | Translating credit-risk context into an analytical workflow |
| Data ingestion | Excel workbook loading, schema review, and record-grain validation |
| Data quality | Missingness review, duplicate checks, invalid-value handling, audit outputs |
| Portfolio monitoring | Segment analysis, exposure analysis, default-rate interpretation |
| Feature engineering | Leakage-safe features, missingness flags, modelling split preparation |
| Modelling | Imbalanced classification, model comparison, validation strategy |
| Threshold selection | Review-cap constraint, cost trade-off, operational decision design |
| Explainability | SHAP, local explanations, rule-style interpretation, sensitivity diagnostics |
| Governance | Model card, validation summary, monitoring plan, control register |

## Notes for GitHub Review

- Raw data is intentionally excluded from the repository.
- Generated outputs should be reviewed for confidentiality before being committed.
- The notebooks should be treated as analytical documentation as well as executable code.
- The final notebook provides the governance wrap-up that connects modelling results to responsible use.
