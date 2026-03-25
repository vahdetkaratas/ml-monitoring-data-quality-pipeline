"""PSI (Population Stability Index). IMPLEMENTATION_REFERENCE §5."""
import numpy as np
import pandas as pd

N_BINS = 10


def psi_numeric(reference: pd.Series, current: pd.Series, n_bins: int = N_BINS) -> float:
    """Compute PSI for a numeric feature. Uses 10 bins from reference percentiles."""
    ref = reference.dropna()
    cur = current.dropna()
    if len(ref) < 2 or len(cur) < 2:
        return 0.0
    breakpoints = np.percentile(ref, np.linspace(0, 100, n_bins + 1)[1:-1])
    breakpoints = np.unique(breakpoints)
    if len(breakpoints) < 2:
        breakpoints = np.percentile(ref, [25, 50, 75])
    bins = np.concatenate(([-np.inf], np.unique(breakpoints), [np.inf]))
    ref_counts = np.histogram(ref, bins=bins)[0]
    cur_counts = np.histogram(cur, bins=bins)[0]
    ref_pct = ref_counts / (ref_counts.sum() + 1e-10)
    cur_pct = cur_counts / (cur_counts.sum() + 1e-10)
    ref_pct = np.clip(ref_pct, 1e-6, 1)
    cur_pct = np.clip(cur_pct, 1e-6, 1)
    psi = np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))
    return float(max(0, psi))


def psi_categorical(reference: pd.Series, current: pd.Series) -> float:
    """PSI for categorical: proportion per category."""
    ref_pct = reference.value_counts(normalize=True)
    cur_pct = current.value_counts(normalize=True)
    all_cats = ref_pct.index.union(cur_pct.index).unique()
    psi = 0.0
    for c in all_cats:
        r = ref_pct.get(c, 1e-6)
        u = cur_pct.get(c, 1e-6)
        r = max(r, 1e-6)
        u = max(u, 1e-6)
        psi += (u - r) * np.log(u / r)
    return float(max(0, psi))
