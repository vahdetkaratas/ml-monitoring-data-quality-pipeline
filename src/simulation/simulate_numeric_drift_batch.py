"""
Simulate current batch with numeric drift (monthly_charges, tenure shifted). MONITORING_SYSTEM_DESIGN §2, MILESTONES M1.
"""
from pathlib import Path
import numpy as np
import pandas as pd

from src.utils.paths import DATA_CURRENT_DIR, REFERENCE_DATASET_CSV

CURRENT_DIR = DATA_CURRENT_DIR


def simulate_numeric_drift_batch(reference_df: pd.DataFrame, seed: int = 45) -> pd.DataFrame:
    """Shift monthly_charges and tenure distributions to trigger drift detection."""
    rng = np.random.default_rng(seed)
    df = reference_df.copy()
    if "monthly_charges" in df.columns:
        # Shift mean up and increase variance
        df["monthly_charges"] = df["monthly_charges"] * (1.2 + rng.normal(0, 0.15, len(df)))
        df["monthly_charges"] = np.clip(df["monthly_charges"], 18, 500)
    if "tenure" in df.columns:
        # Shift tenure distribution (e.g. newer customers)
        df["tenure"] = (df["tenure"] * 0.7 + rng.integers(0, 12, len(df))).astype(int)
        df["tenure"] = np.clip(df["tenure"], 0, 120)
    return df


def run_simulate_numeric_drift(
    reference_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> Path:
    ref_path = Path(reference_path or REFERENCE_DATASET_CSV)
    if not ref_path.exists():
        raise FileNotFoundError(f"Reference not found: {ref_path}.")
    ref = pd.read_csv(ref_path)
    ref_sample = ref.sample(n=min(500, len(ref)), random_state=46).reset_index(drop=True)
    out = simulate_numeric_drift_batch(ref_sample)
    output_path = Path(output_path or CURRENT_DIR / "current_batch_numeric_drift.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    print(f"Numeric drift batch saved: {len(out)} rows -> {output_path}")
    return output_path


if __name__ == "__main__":
    run_simulate_numeric_drift()
