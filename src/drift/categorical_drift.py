"""Categorical drift: PSI, unseen categories. IMPLEMENTATION_REFERENCE §5."""
import pandas as pd
from src.drift.psi import psi_categorical

PSI_HIGH = 0.3
PSI_MEDIUM = 0.2


def categorical_drift_metric(reference: pd.Series, current: pd.Series) -> dict:
    """PSI and unseen count for one categorical column. Returns {psi, unseen_count, severity}."""
    ref_cats = set(reference.dropna().astype(str).unique())
    cur_cats = set(current.dropna().astype(str).unique())
    unseen = len(cur_cats - ref_cats)
    psi = psi_categorical(reference.astype(str), current.astype(str))
    severity = "none"
    if unseen > 0 or psi > PSI_HIGH:
        severity = "high"
    elif psi > PSI_MEDIUM:
        severity = "medium"
    return {"psi": round(psi, 4), "unseen_count": unseen, "severity": severity}
