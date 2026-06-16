# Project Summary

## Canadian Retail Credit Risk Analytics: Explainable Default Prediction, Portfolio Monitoring & Model Governance

This project is an end-to-end credit risk analytics and machine-learning workflow for a Canadian retail lending portfolio. The objective is to identify borrowers with elevated default risk, understand portfolio risk patterns, explain model decisions, and document governance controls suitable for a financial-services environment.

## Business context

Retail lenders need reliable early-warning indicators of default risk. A useful credit-risk solution must support more than prediction accuracy. It must be explainable, auditable, operationally feasible, and aligned with risk-management workflows.

This project treats the model as a decision-support tool for borrower risk ranking and manual-review prioritization. It is not presented as an automated decline, pricing, or adverse-action engine.

## Dataset and target

The dataset contains borrower, loan, employment, income, and credit-behaviour attributes. The target variable is a default indicator. The final modelling dataset contains 134,417 records with an observed default rate of 9.04%.

## Methodology

The workflow includes:

1. Data ingestion from multi-sheet Excel files
2. Record-grain validation to avoid many-to-many merge inflation
3. Data quality assessment and missingness profiling
4. Cleaning, category standardization, and missingness flags
5. Portfolio monitoring and borrower segment analysis
6. Leakage-reviewed feature engineering
7. Model training using logistic regression, random forest, and XGBoost
8. Validation/test evaluation using imbalanced-classification metrics
9. Operating-threshold selection using review-rate and business-cost constraints
10. Explainable AI using SHAP, local explanations, anchor-like rules, and counterfactual diagnostics
11. Model governance documentation and monitoring plan

## Key results

| Area | Result |
|---|---:|
| Portfolio records | 134,417 |
| Observed default rate | 9.04% |
| Champion model | XGBoost weighted classifier |
| Test ROC-AUC | 0.7468 |
| Test PR-AUC | 0.2168 |
| Operating threshold | 0.565 |
| Test recall at threshold | 61.49% |
| Test precision at threshold | 19.10% |
| Test review rate at threshold | 29.11% |

## Business interpretation

At the selected operating threshold, the model captures a meaningful share of default cases while keeping the manual-review population below the project’s operational cap. This is more realistic than relying on the default 0.50 model threshold, which created a larger review population.

Portfolio analysis showed that risk was not evenly distributed across borrower segments. Missing loan amount information, business loans, self-employment, higher interest rates, and loan-to-income patterns were important risk signals.

## Explainability and governance

SHAP identified key risk drivers such as interest rate, missing loan amount flags, data-quality issue counts, income, loan-to-income band, high-interest flags, tenure, loan category, amount, and home ownership. The project also creates local explanations and diagnostic counterfactual scenarios for individual high-risk borrowers.

Governance controls include leakage exclusion, sensitive/proxy-sensitive feature exclusion from the baseline model, validation-based threshold selection, held-out test evaluation, model control register, model risk limits, and monitoring KPIs.

## Portfolio value

This project demonstrates practical skills relevant to Canadian finance roles:

- Credit risk analytics and portfolio monitoring
- Python-based data analysis and modelling
- Imbalanced classification evaluation
- Business threshold optimization
- Explainable AI and stakeholder communication
- Model governance and risk-control documentation
- Clean GitHub project organization with modular code and notebooks
