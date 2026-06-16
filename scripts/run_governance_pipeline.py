from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from credit_risk.config import GOVERNANCE_DIR, PROCESSED_DIR, TABLE_DIR, ensure_project_directories
from credit_risk.governance.model_governance import (
    build_governance_summary,
    build_monitoring_kpi_snapshot,
    load_governance_inputs,
    save_governance_outputs,
)


def main() -> None:
    ensure_project_directories()
    inputs = load_governance_inputs(processed_dir=PROCESSED_DIR, table_dir=TABLE_DIR)
    saved = save_governance_outputs(inputs, table_dir=TABLE_DIR, governance_dir=GOVERNANCE_DIR)

    print("Model-governance pipeline completed")
    print("Governance summary:")
    print(build_governance_summary(inputs).to_string(index=False))
    print("\nMonitoring KPI snapshot:")
    print(build_monitoring_kpi_snapshot(inputs).to_string(index=False))
    print("\nSaved outputs:")
    for name, path in saved.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
