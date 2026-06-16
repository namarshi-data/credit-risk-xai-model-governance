from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

TARGET_COLUMN = "defaulter"


@dataclass
class GovernanceInputs:
    """Container for governance-stage inputs created by earlier notebooks."""

    modeling_df: pd.DataFrame
    feature_catalog: pd.DataFrame
    feature_policy: pd.DataFrame
    split_summary: pd.DataFrame
    validation_results: pd.DataFrame
    test_results: pd.DataFrame
    model_selection: pd.DataFrame
    recommended_threshold: pd.DataFrame
    threshold_shortlist_validation: pd.DataFrame
    threshold_shortlist_test: pd.DataFrame
    cost_assumptions: pd.DataFrame
    xai_grouped_importance: pd.DataFrame
    xai_global_importance: pd.DataFrame
    xai_anchor_rules: pd.DataFrame
    xai_best_counterfactuals: pd.DataFrame
    xai_probability_deciles: pd.DataFrame


def _read_csv(path: Path, required: bool = True) -> pd.DataFrame:
    """Read a CSV and return an empty frame when optional inputs are unavailable."""
    if path.exists():
        return pd.read_csv(path, low_memory=False)
    if required:
        raise FileNotFoundError(
            f"Required governance input not found: {path}. "
            "Run the previous project pipelines before Notebook 09."
        )
    return pd.DataFrame()


def load_governance_inputs(processed_dir: Path, table_dir: Path) -> GovernanceInputs:
    """Load the tables needed for governance documentation."""
    return GovernanceInputs(
        modeling_df=_read_csv(processed_dir / "credit_risk_modeling_dataset.csv"),
        feature_catalog=_read_csv(table_dir / "modeling_feature_catalog.csv"),
        feature_policy=_read_csv(table_dir / "feature_leakage_and_usage_policy.csv"),
        split_summary=_read_csv(table_dir / "modeling_split_distribution.csv"),
        validation_results=_read_csv(table_dir / "model_validation_results_default_threshold.csv"),
        test_results=_read_csv(table_dir / "model_test_results_default_threshold.csv"),
        model_selection=_read_csv(table_dir / "model_selection_summary.csv"),
        recommended_threshold=_read_csv(table_dir / "recommended_threshold_summary.csv"),
        threshold_shortlist_validation=_read_csv(table_dir / "champion_threshold_shortlist_validation.csv"),
        threshold_shortlist_test=_read_csv(table_dir / "champion_threshold_shortlist_test.csv"),
        cost_assumptions=_read_csv(table_dir / "business_cost_assumptions.csv", required=False),
        xai_grouped_importance=_read_csv(table_dir / "xai_grouped_shap_importance.csv"),
        xai_global_importance=_read_csv(table_dir / "xai_global_shap_importance.csv"),
        xai_anchor_rules=_read_csv(table_dir / "xai_anchor_like_rules.csv", required=False),
        xai_best_counterfactuals=_read_csv(table_dir / "xai_best_counterfactual_per_account.csv", required=False),
        xai_probability_deciles=_read_csv(table_dir / "xai_probability_decile_profile.csv", required=False),
    )


def _first_row(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype="object")
    return df.iloc[0]


def _format_pct(value: Any, digits: int = 2) -> str:
    try:
        return f"{float(value) * 100:.{digits}f}%"
    except Exception:
        return "Not available"


def _format_number(value: Any, digits: int = 4) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return "Not available"


def _format_currency(value: Any, digits: int = 0) -> str:
    try:
        return f"${float(value):,.{digits}f}"
    except Exception:
        return "Not available"


def champion_model_name(inputs: GovernanceInputs) -> str:
    """Return the champion model name from model-selection outputs."""
    if inputs.model_selection.empty:
        return "not_available"
    if "selection_rank" in inputs.model_selection.columns:
        row = inputs.model_selection.sort_values("selection_rank").iloc[0]
    else:
        row = inputs.model_selection.iloc[0]
    return str(row.get("model_name", "not_available"))


def recommended_objective(inputs: GovernanceInputs) -> str:
    row = _first_row(inputs.recommended_threshold)
    return str(row.get("objective", "not_available"))


def recommended_threshold_value(inputs: GovernanceInputs) -> float | None:
    row = _first_row(inputs.recommended_threshold)
    if "threshold" not in row:
        return None
    try:
        return float(row["threshold"])
    except Exception:
        return None


def _select_threshold_row(shortlist: pd.DataFrame, objective: str) -> pd.Series:
    if shortlist.empty:
        return pd.Series(dtype="object")
    matched = shortlist.loc[shortlist.get("objective", pd.Series(dtype="object")).eq(objective)]
    if not matched.empty:
        return matched.iloc[0]
    return shortlist.iloc[0]


def build_model_inventory(inputs: GovernanceInputs) -> pd.DataFrame:
    """Create a compact model inventory table for governance documentation."""
    champion = champion_model_name(inputs)
    rec_row = _first_row(inputs.recommended_threshold)
    feature_count = len(inputs.feature_catalog) if not inputs.feature_catalog.empty else None
    modeling_rows = len(inputs.modeling_df)
    default_rate = float(inputs.modeling_df[TARGET_COLUMN].mean()) if TARGET_COLUMN in inputs.modeling_df else None

    return pd.DataFrame(
        [
            {
                "item": "business_use",
                "value": "Early-warning retail credit default-risk ranking and manual-review prioritization",
            },
            {"item": "target", "value": "Defaulter indicator"},
            {"item": "champion_model", "value": champion},
            {"item": "operating_threshold", "value": rec_row.get("threshold", "not_available")},
            {"item": "threshold_objective", "value": rec_row.get("objective", "not_available")},
            {"item": "modeling_rows", "value": modeling_rows},
            {"item": "portfolio_default_rate", "value": default_rate},
            {"item": "model_feature_count", "value": feature_count},
            {"item": "sensitive_proxy_use", "value": "Excluded from baseline model; retained only for audit/governance review where permitted"},
            {"item": "leakage_control", "value": "Repayment-derived variables excluded from model features"},
        ]
    )


def build_validation_test_summary(inputs: GovernanceInputs) -> pd.DataFrame:
    """Create validation/test comparison for the champion model."""
    champion = champion_model_name(inputs)
    objective = recommended_objective(inputs)

    validation_default = inputs.validation_results.loc[
        inputs.validation_results.get("model_name", pd.Series(dtype="object")).eq(champion)
    ].copy()
    test_default = inputs.test_results.loc[
        inputs.test_results.get("model_name", pd.Series(dtype="object")).eq(champion)
    ].copy()

    validation_operating = _select_threshold_row(inputs.threshold_shortlist_validation, objective).to_frame().T
    test_operating = _select_threshold_row(inputs.threshold_shortlist_test, objective).to_frame().T

    frames = []
    if not validation_default.empty:
        row = validation_default.iloc[0].to_dict()
        row.update({"evaluation_view": "validation_default_0_50", "selected_operating_threshold": False})
        frames.append(row)
    if not test_default.empty:
        row = test_default.iloc[0].to_dict()
        row.update({"evaluation_view": "test_default_0_50", "selected_operating_threshold": False})
        frames.append(row)
    if not validation_operating.empty:
        row = validation_operating.iloc[0].to_dict()
        row.update({"evaluation_view": "validation_selected_operating_threshold", "selected_operating_threshold": True})
        frames.append(row)
    if not test_operating.empty:
        row = test_operating.iloc[0].to_dict()
        row.update({"evaluation_view": "test_selected_operating_threshold", "selected_operating_threshold": True})
        frames.append(row)

    summary = pd.DataFrame(frames)
    wanted = [
        "evaluation_view",
        "model_name",
        "dataset",
        "threshold",
        "roc_auc",
        "pr_auc",
        "brier_score",
        "recall",
        "precision",
        "f1",
        "balanced_accuracy",
        "mcc",
        "review_rate",
        "business_cost",
        "false_negative",
        "false_positive",
        "true_positive",
        "true_negative",
        "selected_operating_threshold",
    ]
    return summary[[c for c in wanted if c in summary.columns]]


def build_feature_governance_summary(inputs: GovernanceInputs) -> pd.DataFrame:
    """Summarize feature use and exclusions from the leakage policy."""
    if inputs.feature_policy.empty:
        return pd.DataFrame()
    policy = inputs.feature_policy.copy()
    group_cols = [col for col in ["model_usage", "governance_decision", "reason"] if col in policy.columns]
    if not group_cols:
        return pd.DataFrame({"feature_count": [len(policy)]})
    summary = policy.groupby(group_cols, dropna=False).size().reset_index(name="feature_count")
    return summary.sort_values("feature_count", ascending=False).reset_index(drop=True)


def build_xai_governance_summary(inputs: GovernanceInputs, top_n: int = 12) -> pd.DataFrame:
    """Return top XAI drivers with governance interpretation notes."""
    if inputs.xai_grouped_importance.empty:
        return pd.DataFrame()
    xai = inputs.xai_grouped_importance.head(top_n).copy()

    def note(feature: str) -> str:
        feature = str(feature)
        if "data_quality" in feature or "missing" in feature:
            return "Data-quality signal: monitor for drift and do not interpret as borrower behaviour alone."
        if feature in {"interest_rate", "high_interest_flag", "interest_rate_x_lti"}:
            return "Pricing/risk signal: explain carefully because pricing can reflect prior underwriting risk."
        if feature in {"total_income_pa", "loan_to_income_ratio", "loan_to_income_band", "amount"}:
            return "Affordability/exposure signal: suitable for portfolio-risk interpretation."
        if feature in {"loan_category", "home", "tenure_years"}:
            return "Segment/product signal: monitor segment stability and business reasonableness."
        return "Review for business reasonableness and stability."

    feature_column = "raw_feature" if "raw_feature" in xai.columns else xai.columns[0]
    xai["governance_note"] = xai[feature_column].map(note)
    return xai


def build_control_register() -> pd.DataFrame:
    """Create a professional model-risk control register."""
    rows = [
        {
            "control_area": "Data ingestion",
            "risk": "Many-to-many sheet merge inflates borrower records and changes target rate.",
            "control": "Merge sheets using user_id plus record_sequence and test duplicate record keys.",
            "evidence": "Notebook 01 ingestion summary and record-key duplicate check.",
            "owner": "Risk analytics",
            "frequency": "Each data refresh",
        },
        {
            "control_area": "Data quality",
            "risk": "Missing amount/employment fields may distort score interpretation.",
            "control": "Create missingness flags, monitor missingness rates, and retain data-quality features only where justified.",
            "evidence": "Notebook 02/03 missingness and data-quality flag summaries.",
            "owner": "Data analyst / data steward",
            "frequency": "Monthly",
        },
        {
            "control_area": "Leakage prevention",
            "risk": "Repayment-derived variables can leak target information into model training.",
            "control": "Exclude total_payment, received_principal, interest_received, and derived repayment ratios from model features.",
            "evidence": "Feature leakage and usage policy table.",
            "owner": "Model developer",
            "frequency": "Before each model release",
        },
        {
            "control_area": "Fairness and proxy risk",
            "risk": "Sensitive/proxy variables could create unfair or hard-to-defend decisions.",
            "control": "Exclude gender, marital status, pincode, and social profile from baseline model; retain only for approved audit review.",
            "evidence": "Feature policy and model feature catalogue.",
            "owner": "Model governance / compliance partner",
            "frequency": "Before release and annually",
        },
        {
            "control_area": "Model performance",
            "risk": "Model ranking weakens or becomes unstable after deployment.",
            "control": "Monitor PR-AUC, ROC-AUC, recall, precision, Brier score, and confusion-matrix outcomes when labels mature.",
            "evidence": "Notebook 06 validation/test results.",
            "owner": "Model monitoring team",
            "frequency": "Monthly/quarterly",
        },
        {
            "control_area": "Threshold governance",
            "risk": "Operating threshold overloads manual review teams or misses too many defaults.",
            "control": "Select threshold on validation data using business-cost and review-cap constraints; validate once on test data.",
            "evidence": "Notebook 07 threshold shortlist and recommended threshold summary.",
            "owner": "Credit-risk strategy",
            "frequency": "Quarterly or after material portfolio change",
        },
        {
            "control_area": "Explainability",
            "risk": "Stakeholders cannot understand why accounts are sent to review.",
            "control": "Provide global SHAP drivers, local reason codes, anchor-like rules, and counterfactual scenario diagnostics.",
            "evidence": "Notebook 08 XAI outputs.",
            "owner": "Risk analytics / model validation",
            "frequency": "Each model release",
        },
        {
            "control_area": "Ongoing monitoring",
            "risk": "Population, score, or data-quality drift changes model behaviour.",
            "control": "Track score distribution, review rate, feature missingness, top-driver PSI, and realized default outcomes.",
            "evidence": "Notebook 09 monitoring plan and risk-limit register.",
            "owner": "Model owner",
            "frequency": "Monthly",
        },
    ]
    return pd.DataFrame(rows)


def build_model_risk_limit_register(inputs: GovernanceInputs) -> pd.DataFrame:
    """Create illustrative risk limits for portfolio monitoring."""
    objective = recommended_objective(inputs)
    test_row = _select_threshold_row(inputs.threshold_shortlist_test, objective)
    review_rate = test_row.get("review_rate", None)
    recall = test_row.get("recall", None)
    precision = test_row.get("precision", None)

    def warn_floor(value: Any, offset: float) -> str:
        try:
            return f"< {max(float(value) - offset, 0):.2%}"
        except Exception:
            return "Define after first production benchmark"

    def warn_ceiling(value: Any, offset: float) -> str:
        try:
            return f"> {min(float(value) + offset, 1):.2%}"
        except Exception:
            return "Define after first production benchmark"

    rows = [
        {
            "metric": "Population Stability Index - overall score",
            "baseline": "Training/test score distribution",
            "warning_limit": "> 0.10",
            "breach_limit": "> 0.25",
            "monitoring_frequency": "Monthly",
            "action": "Investigate portfolio shift, data pipeline changes, and score calibration.",
        },
        {
            "metric": "Key feature PSI - top SHAP drivers",
            "baseline": "Training/test feature distributions",
            "warning_limit": "> 0.10",
            "breach_limit": "> 0.25",
            "monitoring_frequency": "Monthly",
            "action": "Review feature distribution shift and retraining need.",
        },
        {
            "metric": "Operating review rate",
            "baseline": _format_pct(review_rate),
            "warning_limit": warn_ceiling(review_rate, 0.05),
            "breach_limit": warn_ceiling(review_rate, 0.10),
            "monitoring_frequency": "Weekly/monthly",
            "action": "Review threshold capacity and manual-review staffing impact.",
        },
        {
            "metric": "Recall on matured labels",
            "baseline": _format_pct(recall),
            "warning_limit": warn_floor(recall, 0.05),
            "breach_limit": warn_floor(recall, 0.10),
            "monitoring_frequency": "Monthly after labels mature",
            "action": "Assess missed-default concentration and model refresh need.",
        },
        {
            "metric": "Precision on reviewed accounts",
            "baseline": _format_pct(precision),
            "warning_limit": warn_floor(precision, 0.03),
            "breach_limit": warn_floor(precision, 0.05),
            "monitoring_frequency": "Monthly after labels mature",
            "action": "Review false-positive burden and customer-impact risk.",
        },
        {
            "metric": "Critical data-quality missingness",
            "baseline": "Notebook 02/03 data-quality profile",
            "warning_limit": "+25% relative increase",
            "breach_limit": "+50% relative increase",
            "monitoring_frequency": "Each data load",
            "action": "Open data-quality incident and pause model refresh if severe.",
        },
    ]
    return pd.DataFrame(rows)


def build_monitoring_kpi_snapshot(inputs: GovernanceInputs) -> pd.DataFrame:
    """Create an initial KPI snapshot for Notebook 09."""
    objective = recommended_objective(inputs)
    threshold = recommended_threshold_value(inputs)
    champion = champion_model_name(inputs)
    test_row = _select_threshold_row(inputs.threshold_shortlist_test, objective)
    validation_row = _select_threshold_row(inputs.threshold_shortlist_validation, objective)

    model_default_row = inputs.test_results.loc[
        inputs.test_results.get("model_name", pd.Series(dtype="object")).eq(champion)
    ]
    model_default_row = _first_row(model_default_row)

    default_rate = inputs.modeling_df[TARGET_COLUMN].mean() if TARGET_COLUMN in inputs.modeling_df else None
    top_features = []
    if not inputs.xai_grouped_importance.empty:
        feature_col = "raw_feature" if "raw_feature" in inputs.xai_grouped_importance.columns else inputs.xai_grouped_importance.columns[0]
        top_features = inputs.xai_grouped_importance[feature_col].head(5).astype(str).tolist()

    rows = [
        {"kpi": "Champion model", "value": champion, "interpretation": "Selected using validation ranking metrics."},
        {"kpi": "Portfolio default rate", "value": _format_pct(default_rate), "interpretation": "Base rate for interpreting precision and review workload."},
        {"kpi": "Recommended objective", "value": objective, "interpretation": "Threshold-selection business rule."},
        {"kpi": "Operating threshold", "value": _format_number(threshold, 3), "interpretation": "Probability cutoff for manual-review flag."},
        {"kpi": "Test ROC-AUC", "value": _format_number(model_default_row.get("roc_auc"), 4), "interpretation": "Out-of-sample ranking performance."},
        {"kpi": "Test PR-AUC", "value": _format_number(model_default_row.get("pr_auc"), 4), "interpretation": "Ranking performance under class imbalance."},
        {"kpi": "Validation recall at operating threshold", "value": _format_pct(validation_row.get("recall")), "interpretation": "Defaults captured during threshold selection."},
        {"kpi": "Test recall at operating threshold", "value": _format_pct(test_row.get("recall")), "interpretation": "Out-of-sample defaults captured at selected threshold."},
        {"kpi": "Test precision at operating threshold", "value": _format_pct(test_row.get("precision")), "interpretation": "Share of reviewed accounts that defaulted."},
        {"kpi": "Test review rate at operating threshold", "value": _format_pct(test_row.get("review_rate")), "interpretation": "Operational workload from the score cutoff."},
        {"kpi": "Test illustrative business cost", "value": _format_currency(test_row.get("business_cost")), "interpretation": "Scenario cost using Notebook 07 assumptions."},
        {"kpi": "Top SHAP drivers", "value": ", ".join(top_features), "interpretation": "Primary explanation drivers to monitor for drift."},
    ]
    return pd.DataFrame(rows)


def build_governance_summary(inputs: GovernanceInputs) -> pd.DataFrame:
    """Create a one-row governance summary suitable for README/reporting."""
    objective = recommended_objective(inputs)
    threshold = recommended_threshold_value(inputs)
    test_row = _select_threshold_row(inputs.threshold_shortlist_test, objective)
    champion = champion_model_name(inputs)
    default_rate = inputs.modeling_df[TARGET_COLUMN].mean() if TARGET_COLUMN in inputs.modeling_df else None

    return pd.DataFrame(
        [
            {
                "champion_model": champion,
                "modeling_rows": len(inputs.modeling_df),
                "portfolio_default_rate": default_rate,
                "operating_threshold": threshold,
                "threshold_objective": objective,
                "test_recall": test_row.get("recall"),
                "test_precision": test_row.get("precision"),
                "test_review_rate": test_row.get("review_rate"),
                "test_business_cost": test_row.get("business_cost"),
                "primary_governance_decision": "Use as decision-support/manual-review prioritization model, not as an automated credit-decline engine.",
            }
        ]
    )


def _markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if df.empty:
        return "Not available."
    out = df.head(max_rows).copy() if max_rows else df.copy()
    return out.to_markdown(index=False)


def write_model_card(inputs: GovernanceInputs, output_path: Path) -> None:
    """Write a markdown model card."""
    inventory = build_model_inventory(inputs)
    perf = build_validation_test_summary(inputs)
    xai = build_xai_governance_summary(inputs, top_n=10)
    limits = build_model_risk_limit_register(inputs)

    champion = champion_model_name(inputs)
    threshold = recommended_threshold_value(inputs)
    objective = recommended_objective(inputs)

    text = f"""# Model Card - Canadian Retail Credit Risk XAI

## Model overview

- **Business purpose:** Early-warning retail credit default-risk ranking and manual-review prioritization.
- **Champion model:** `{champion}`
- **Operating threshold:** `{_format_number(threshold, 3)}`
- **Threshold objective:** `{objective}`
- **Target:** borrower default indicator.
- **Intended use:** decision support for portfolio monitoring and risk review.
- **Out-of-scope use:** automated credit decline, pricing decisioning, or adverse-action communication without additional validation, legal review, and fairness assessment.

## Model inventory

{_markdown_table(inventory)}

## Validation and test performance

{_markdown_table(perf)}

## Top explainability drivers

{_markdown_table(xai, max_rows=10)}

## Key controls

- Repayment-derived variables are excluded from the modelling feature set to reduce target leakage risk.
- Sensitive/proxy-sensitive attributes are excluded from the baseline model and retained only for permitted audit/governance review.
- The operating threshold is selected on validation data and reviewed once on the held-out test split.
- Counterfactual scenarios are diagnostic only and should not be interpreted as customer instructions.

## Monitoring limits

{_markdown_table(limits)}
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def write_validation_summary(inputs: GovernanceInputs, output_path: Path) -> None:
    """Write model-validation summary markdown."""
    summary = build_governance_summary(inputs)
    perf = build_validation_test_summary(inputs)
    controls = build_control_register()
    feature_gov = build_feature_governance_summary(inputs)

    text = f"""# Model Validation Summary

## Executive summary

This project develops a leakage-reviewed, explainable default-risk model for a Canadian retail credit portfolio. The model is positioned as a **manual-review prioritization and portfolio-monitoring tool**, not as an automated decline engine.

{_markdown_table(summary)}

## Performance evidence

{_markdown_table(perf)}

## Feature governance

{_markdown_table(feature_gov)}

## Control register

{_markdown_table(controls)}

## Validation decision

The model is acceptable for portfolio analytics and decision-support demonstration purposes, subject to the monitoring plan and the limitations documented here. Before production use, the model would require independent validation, data lineage review, calibration review, fairness testing, privacy/legal review, and user-acceptance testing with credit-risk stakeholders.
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def write_stakeholder_brief(inputs: GovernanceInputs, output_path: Path) -> None:
    """Write a non-technical stakeholder summary."""
    summary = build_governance_summary(inputs).iloc[0]
    xai = build_xai_governance_summary(inputs, top_n=5)

    text = f"""# Stakeholder Brief - Retail Credit Default-Risk Model

## What the model does

The model ranks borrowers by estimated default risk so that a credit-risk team can prioritize manual review and portfolio monitoring.

## Recommended operating point

- **Champion model:** {summary.get('champion_model')}
- **Operating threshold:** {_format_number(summary.get('operating_threshold'), 3)}
- **Test recall:** {_format_pct(summary.get('test_recall'))}
- **Test precision:** {_format_pct(summary.get('test_precision'))}
- **Test review rate:** {_format_pct(summary.get('test_review_rate'))}

## Business interpretation

At the selected threshold, the model captures a meaningful share of future defaults while keeping the review population below the operational cap used in this project. This makes it more practical than using the default 0.50 cutoff.

## Main risk drivers identified by explainability

{_markdown_table(xai, max_rows=5)}

## How this should be used

Use the score to support analyst review, portfolio segmentation, and monitoring. Do not use it as a standalone automated lending decision without additional validation, fairness testing, compliance review, and production monitoring.
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def write_monitoring_plan(inputs: GovernanceInputs, output_path: Path) -> None:
    """Write a model monitoring plan."""
    kpis = build_monitoring_kpi_snapshot(inputs)
    limits = build_model_risk_limit_register(inputs)

    text = f"""# Model Monitoring Plan

## Monitoring objective

Ensure the credit-risk model remains stable, explainable, and operationally useful after deployment or future data refreshes.

## KPI snapshot

{_markdown_table(kpis)}

## Risk limits and escalation triggers

{_markdown_table(limits)}

## Suggested monitoring cadence

- **Each data refresh:** schema checks, duplicate-key checks, missingness checks, and leakage-policy checks.
- **Monthly:** score distribution, review rate, feature drift, data-quality drift, top-SHAP-driver drift.
- **After labels mature:** realized default rate, recall, precision, false negatives, and false positives.
- **Quarterly or material-change event:** threshold review, model challenger review, governance sign-off.

## Escalation actions

If a breach occurs, pause automated refreshes if necessary, document the issue, identify root cause, quantify borrower/business impact, and decide whether remediation, recalibration, threshold adjustment, or retraining is required.
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def save_governance_outputs(inputs: GovernanceInputs, table_dir: Path, governance_dir: Path) -> dict[str, str]:
    """Save governance tables and markdown documents."""
    table_dir.mkdir(parents=True, exist_ok=True)
    governance_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "model_inventory": build_model_inventory(inputs),
        "model_validation_test_summary": build_validation_test_summary(inputs),
        "feature_governance_summary": build_feature_governance_summary(inputs),
        "xai_governance_summary": build_xai_governance_summary(inputs),
        "model_control_register": build_control_register(),
        "model_risk_limit_register": build_model_risk_limit_register(inputs),
        "model_monitoring_kpi_snapshot": build_monitoring_kpi_snapshot(inputs),
        "model_governance_summary": build_governance_summary(inputs),
    }

    saved: dict[str, str] = {}
    for name, df in outputs.items():
        path = table_dir / f"{name}.csv"
        df.to_csv(path, index=False)
        saved[name] = str(path)

    markdown_outputs = {
        "model_card": governance_dir / "model_card.md",
        "model_validation_summary": governance_dir / "model_validation_summary.md",
        "stakeholder_brief": governance_dir / "stakeholder_brief.md",
        "model_monitoring_plan": governance_dir / "model_monitoring_plan.md",
    }
    write_model_card(inputs, markdown_outputs["model_card"])
    write_validation_summary(inputs, markdown_outputs["model_validation_summary"])
    write_stakeholder_brief(inputs, markdown_outputs["stakeholder_brief"])
    write_monitoring_plan(inputs, markdown_outputs["model_monitoring_plan"])
    saved.update({name: str(path) for name, path in markdown_outputs.items()})
    return saved
