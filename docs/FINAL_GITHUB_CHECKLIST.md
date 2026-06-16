# Final GitHub Checklist

## Files to review before publishing

- [ ] README.md
- [ ] docs/PROJECT_SUMMARY.md
- [ ] docs/INTERVIEW_TALKING_POINTS.md
- [ ] docs/GITHUB_PRESENTATION_GUIDE.md
- [ ] docs/PORTFOLIO_SNIPPETS.md
- [ ] notebooks/00_project_brief_and_business_context.ipynb
- [ ] notebooks/01_data_ingestion_and_schema_review.ipynb
- [ ] notebooks/02_data_quality_assessment.ipynb
- [ ] notebooks/03_data_cleaning_and_preprocessing.ipynb
- [ ] notebooks/04_credit_risk_eda_and_portfolio_monitoring.ipynb
- [ ] notebooks/05_feature_engineering_and_leakage_review.ipynb
- [ ] notebooks/06_model_training_and_evaluation.ipynb
- [ ] notebooks/07_threshold_selection_and_business_costing.ipynb
- [ ] notebooks/08_explainable_ai_shap_anchors_counterfactuals.ipynb
- [ ] notebooks/09_model_governance_and_monitoring.ipynb

## Do not commit

- [ ] data/raw/Credit_Risk_Dataset.xlsx
- [ ] data/interim/*.csv
- [ ] data/processed/*.csv
- [ ] reports/model_artifacts/*.joblib
- [ ] .venv/
- [ ] .env
- [ ] __pycache__/
- [ ] .ipynb_checkpoints/

## Commit command

Use `git status` before staging. Then stage only safe files.

```bash
git add README.md docs/ notebooks/ src/ scripts/ config/ reports/figures/ reports/governance/ reports/tables/ requirements.txt pyproject.toml .gitignore LICENSE .github/
git status
git commit -m "Complete Canadian retail credit risk XAI portfolio project"
```

If `git status` shows raw data, processed data, or model binaries, unstage them before committing.

```bash
git restore --staged data/raw data/interim data/processed reports/model_artifacts
```
