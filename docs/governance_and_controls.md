# Governance and Controls

## Purpose

This document summarizes the model-governance, data-quality, leakage-control, and responsible-use decisions for the Retail Credit Risk Analytics project.

The project is framed as a default-risk ranking and manual-review prioritization workflow. It is not an automated credit approval or decline engine.

## Governance Positioning

| Governance area | Project position |
|---|---|
| Intended use | Manual-review prioritization and portfolio monitoring |
| Prohibited use | Automated credit approval, automated decline, or customer-facing decisioning |
| Business owner | Credit risk / portfolio analytics team |
| Model user | Analyst or risk-review team |
| Required production approval | Model risk, privacy/legal, data governance, and business owner sign-off |

## Data Quality and Modelling Decisions

| Area | Decision |
|---|---|
| Record grain | Preserve row-level sequencing to avoid many-to-many merge inflation |
| Missing values | Create missingness flags before imputation |
| Invalid values | Review non-positive loan amounts and convert invalid values to missing where appropriate |
| High-cardinality fields | Avoid direct one-hot encoding of very high-cardinality variables |
| Geographic proxy risk | Exclude geographic proxy fields from the baseline model unless governance justification exists |
| Sensitive attributes | Exclude sensitive attributes from predictive features |
| Leakage prevention | Exclude repayment-derived and target-adjacent fields from baseline modelling |
| Model evaluation | Use validation data for model and threshold selection; reserve test data for final confirmation |
| Responsible use | Use model output for manual-review prioritization, not automated credit decline |

## Control Register

| Control area | Control decision | Why it matters |
|---|---|---|
| Record-grain control | Preserve borrower record sequencing and audit keys | Prevents duplicate or inflated records during joins |
| Data-quality control | Retain missingness indicators and document data limitations | Supports auditability and operational interpretation |
| Leakage control | Exclude repayment-derived and target-adjacent variables | Prevents the model from learning information unavailable at prediction time |
| Sensitive/proxy control | Exclude sensitive and high-risk proxy variables from baseline model | Reduces governance and fairness risk |
| Model-selection control | Select models using validation data only | Prevents overfitting to the final test set |
| Threshold-control | Select threshold using review-cap and cost assumptions | Connects model output to operational capacity |
| Test-data control | Use test data once for final confirmation | Preserves independent performance evidence |
| Explainability control | Provide global and local explanations for review | Supports stakeholder understanding and auditability |
| Monitoring control | Define drift, performance, review-rate, and data-quality monitoring limits | Supports ongoing model oversight |
| Use restriction | Limit use to decision support and manual-review prioritization | Prevents inappropriate automated decisioning |

## Governance Outputs

| Output | Purpose |
|---|---|
| `reports/governance/model_card.md` | Summarizes model purpose, intended use, performance, explainability, limitations, and controls |
| `reports/governance/model_validation_summary.md` | Documents validation/test evidence and governance decision |
| `reports/governance/stakeholder_brief.md` | Explains model performance and business use in non-technical language |
| `reports/governance/model_monitoring_plan.md` | Defines monitoring cadence, KPIs, risk limits, and escalation actions |
| `reports/tables/model_control_register.csv` | Lists model-risk controls and ownership |
| `reports/tables/model_risk_limit_register.csv` | Defines monitoring thresholds and breach actions |
| `reports/tables/model_monitoring_kpi_snapshot.csv` | Provides initial monitoring baseline |
| `reports/tables/model_governance_summary.csv` | Provides executive governance summary |

## Monitoring Plan

The project assumes the model would require ongoing monitoring before any real business use.

| Monitoring area | Example KPI |
|---|---|
| Data quality | Missing values, invalid values, schema changes, duplicate keys |
| Population stability | Feature distribution drift and borrower mix changes |
| Model performance | ROC-AUC, PR-AUC, recall, precision, calibration, review-rate trend |
| Operational workload | Share of borrowers crossing the review threshold |
| Risk concentration | Default-risk distribution by borrower, loan, and exposure segment |
| Responsible use | Confirmation that outputs remain decision-support only |

## Production Readiness Requirements

Before any real financial-institution use, this model would require:

- Independent validation
- Out-of-time testing
- Fairness and bias testing
- Calibration review
- Privacy and consent review
- Legal and compliance review
- Model-risk approval
- Monitoring automation
- Incident and escalation process
- Business owner sign-off

## Responsible-Use Statement

The model output should be used only to prioritize borrower records for analyst review and portfolio monitoring. It should not be used as a direct customer instruction, adverse-action reason, automatic decline decision, or standalone credit decision.
