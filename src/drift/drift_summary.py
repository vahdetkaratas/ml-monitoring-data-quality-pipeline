"""Run drift analysis: reference vs current batch. MILESTONES M3."""
from pathlib import Path
import pandas as pd
from src.drift.numeric_drift import numeric_drift_metric
from src.drift.categorical_drift import categorical_drift_metric

NUMERIC_COLS = ["tenure", "monthly_charges", "total_charges", "num_active_services", "senior_citizen", "churn_score"]
CATEGORICAL_COLS = ["contract", "internet_service", "payment_method"]


def compute_drift_summary(reference_df: pd.DataFrame, current_df: pd.DataFrame) -> dict:
    """Compute drift per column; aggregate high/medium counts. Returns {status, high_count, medium_count, per_column}."""
    per_column = {}
    high_count = 0
    medium_count = 0
    for col in NUMERIC_COLS:
        if col not in reference_df.columns or col not in current_df.columns:
            continue
        m = numeric_drift_metric(reference_df[col], current_df[col])
        per_column[col] = m
        if m["severity"] == "high":
            high_count += 1
        elif m["severity"] == "medium":
            medium_count += 1
    for col in CATEGORICAL_COLS:
        if col not in reference_df.columns or col not in current_df.columns:
            continue
        m = categorical_drift_metric(reference_df[col], current_df[col])
        per_column[col] = m
        if m["severity"] == "high":
            high_count += 1
        elif m["severity"] == "medium":
            medium_count += 1
    status = "ok"
    if high_count > 0:
        status = "critical"
    elif medium_count > 0:
        status = "warning"
    return {"status": status, "high_count": high_count, "medium_count": medium_count, "per_column": per_column}
