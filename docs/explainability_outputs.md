# Explainability Outputs

## Purpose

This document summarizes the explainable AI outputs produced for the Retail Credit Risk Analytics project. The explainability layer is designed to help analysts, risk stakeholders, and model-governance reviewers understand why the model ranks certain borrowers as higher risk.

The explanations are intended for analyst review and model understanding only. They should not be treated as automatic customer-facing adverse-action reasons.

## Explainability Methods

| Method | Purpose |
|---|---|
| Global SHAP feature importance | Identifies the strongest overall model drivers |
| Grouped SHAP drivers | Summarizes related features into business-readable driver groups |
| SHAP dependence-style plots | Shows how specific features influence predicted risk across value ranges |
| Borrower-level local explanations | Explains model drivers for individual reviewed borrowers |
| Anchor-style high-risk rules | Produces simplified rule-style patterns associated with elevated risk |
| Counterfactual sensitivity scenarios | Tests how predicted risk changes under hypothetical feature changes |
| Deepchecks model evaluation report | Supports additional diagnostic review |
| Stakeholder metric interpretation table | Translates technical outputs into business-readable language |

## Business Use

Explainability outputs support three practical questions:

1. Which features are most associated with elevated default-risk scores?
2. Why was a specific borrower ranked higher or lower risk by the model?
3. Which patterns should analysts monitor when reviewing high-risk accounts?

## Global Explainability

Global explanations help stakeholders understand the main risk drivers across the portfolio. These outputs are useful for:

- Validating whether model drivers are directionally reasonable
- Identifying potential proxy-risk concerns
- Reviewing whether model behaviour aligns with credit-risk intuition
- Communicating model behaviour to non-technical stakeholders

Recommended output examples:

```text
reports/figures/08_xai_global_grouped_shap_top_features.png
reports/tables/xai_global_feature_importance.csv
reports/tables/xai_grouped_driver_summary.csv
```

## Local Explainability

Local explanations are used for borrower-level review. They help explain why a borrower receives a higher or lower risk score based on the model's learned patterns.

Recommended output examples:

```text
reports/tables/xai_local_explanations_sample.csv
reports/tables/stakeholder_metric_interpretation.csv
```

## Anchor-Style Rules

Anchor-style rules provide simplified high-risk patterns that are easier to discuss with business users than raw model coefficients or SHAP values.

These rules are useful for analyst understanding, but they should not replace the full model or be used as direct customer instructions.

## Counterfactual Diagnostics

Counterfactual sensitivity scenarios show how model scores may change under hypothetical feature changes. They are useful for model-sensitivity review and stakeholder education.

Important limitation:

> Counterfactuals are diagnostic model-sensitivity scenarios and should not be used as direct customer instructions or adverse-action reasons.

## Governance Considerations

Explainability outputs should be reviewed alongside data-quality and model-risk controls.

| Governance concern | Review action |
|---|---|
| Sensitive attributes | Confirm sensitive attributes are excluded from predictive features |
| Proxy variables | Review features that may indirectly represent protected or sensitive characteristics |
| Leakage | Confirm repayment-derived and target-adjacent fields are excluded |
| Stability | Monitor whether feature importance changes materially over time |
| Interpretability | Validate that explanations are understandable to business stakeholders |
| Responsible use | Confirm explanations support manual review, not automated decisioning |

## Recommended Interview Talking Points

1. Why SHAP was used to support global and borrower-level explanation.
2. How explanations improve trust but do not remove the need for model governance.
3. Why counterfactuals are diagnostic and not customer-facing recommendations.
4. How explanation outputs can support model validation and stakeholder review.
5. How feature drivers should be monitored over time for drift and proxy-risk concerns.

## Summary

The explainability layer strengthens the project by showing not only model performance, but also model behaviour. This is important for credit-risk analytics because financial-services models must be interpretable, monitored, and governed before they can support real business decisions.
