# GitHub Presentation Guide

## Repository name

```text
canadian-retail-credit-risk-xai
```

## Repository description

```text
End-to-end Canadian retail credit risk analytics project covering default prediction, portfolio monitoring, explainable AI, threshold optimization, and model governance.
```

## Suggested GitHub topics

```text
credit-risk
risk-analytics
machine-learning
xgboost
random-forest
explainable-ai
shap
model-governance
portfolio-monitoring
python
banking-analytics
```

## What to pin in the README

Place these near the top:

1. Business problem
2. Key results table
3. Workflow diagram
4. Three figures: portfolio target distribution, default rate by loan category, SHAP feature importance
5. Notebook workflow table
6. Governance outputs
7. Limitations and intended use

## What to commit

Commit:

- Source code under `src/credit_risk/`
- Notebooks with outputs saved
- `README.md`
- `docs/`
- Generated non-sensitive figures under `reports/figures/`
- Governance markdown outputs under `reports/governance/`
- Selected summary CSV tables under `reports/tables/` if they do not expose restricted raw data

Do not commit:

- Raw Excel workbook
- Interim or processed datasets
- Model binaries such as `.joblib` or `.pkl`
- Environment folders
- Secrets or API keys

## Suggested first commit after final polish

```bash
git add README.md docs/ reports/governance/ reports/figures/ notebooks/ src/ scripts/ config/ tests/ requirements.txt pyproject.toml .gitignore
git commit -m "Complete credit risk modelling, XAI, and governance portfolio project"
```

Before running the command, check `git status` and make sure no raw data or model artifacts are staged.

## GitHub README image order

Recommended order:

```markdown
![Portfolio target distribution](reports/figures/portfolio_target_distribution.png)
![Default rate by loan category](reports/figures/default_rate_by_loan_category.png)
![Global SHAP feature importance](reports/figures/xai_global_shap_top_features.png)
```

## Final quality checklist

- [ ] `README.md` renders cleanly on GitHub
- [ ] All notebooks run in order from `00` to `09`
- [ ] No raw data is committed
- [ ] No `.joblib`, `.pkl`, `.env`, or virtual environment files are committed
- [ ] Notebook outputs show the final operating threshold and governance summary
- [ ] Figures render in the README
- [ ] Governance markdown files are readable
- [ ] Repo About section and topics are filled out
- [ ] Project is pinned on GitHub profile
- [ ] Resume includes one concise project bullet set
