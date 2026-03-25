"""Numeric drift: KS test, PSI. IMPLEMENTATION_REFERENCE §5."""
import pandas as pd
from scipy import stats
from src.drift.psi import psi_numeric

PSI_HIGH = 0.3
PSI_MEDIUM = 0.2
KS_P_HIGH = 0.01
KS_P_MEDIUM = 0.05


def ks_test(reference: pd.Series, current: pd.Series) -> tuple[float, float]:
    """KS statistic and p-value. Returns (statistic, pvalue)."""
    ref = reference.dropna()
    cur = current.dropna()
    if len(ref) < 2 or len(cur) < 2:
        return 0.0, 1.0
    res = stats.ks_2samp(ref, cur)
    return float(res.statistic), float(res.pvalue)


def numeric_drift_metric(reference: pd.Series, current: pd.Series) -> dict:
    """Compute PSI and KS for one numeric column. Returns {psi, ks_stat, ks_pvalue, severity}."""
    psi = psi_numeric(reference, current)
    ks_stat, ks_p = ks_test(reference, current)
    severity = "none"
    if psi > PSI_HIGH or ks_p < KS_P_HIGH:
        severity = "high"
    elif psi > PSI_MEDIUM or ks_p < KS_P_MEDIUM:
        severity = "medium"
    return {"psi": round(psi, 4), "ks_statistic": round(ks_stat, 4), "ks_pvalue": round(ks_p, 4), "severity": severity}
