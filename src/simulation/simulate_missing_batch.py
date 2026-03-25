"""
Simulate current batch with elevated missing rate. MONITORING_SYSTEM_DESIGN §2, MILESTONES M1.
"""
from pathlib import Path
import numpy as np
import pandas as pd

from src.utils.paths import DATA_CURRENT_DIR, REFERENCE_DATASET_CSV

CURRENT_DIR = DATA_CURRENT_DIR
MISSING_FRACTION = 0.15  # 15% of values in some columns set to NaN


def simulate_missing_batch(reference_df: pd.DataFrame, missing_frac: float = MISSING_FRACTION, seed: int = 43) -> pd.DataFrame:
    """Add missing values to a subset of columns to trigger validation alarm."""
    rng = np.random.default_rng(seed)
    df = reference_df.copy()
    cols_to_missing = ["monthly_charges", "total_charges", "num_active_services"]
    for col in cols_to_missing:
        if col not in df.columns:
            continue
        mask = rng.random(len(df)) < missing_frac
        df.loc[mask, col] = np.nan
    return df


def run_simulate_missing(
    reference_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> Path:
    ref_path = Path(reference_path or REFERENCE_DATASET_CSV)
    if not ref_path.exists():
        raise FileNotFoundError(f"Reference not found: {ref_path}. Run build_reference_dataset first.")
    ref = pd.read_csv(ref_path)
    # Use a sample for "current" batch (e.g. 500 rows)
    ref_sample = ref.sample(n=min(500, len(ref)), random_state=44).reset_index(drop=True)
    out = simulate_missing_batch(ref_sample)
    output_path = Path(output_path or CURRENT_DIR / "current_batch_missing.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    print(f"Missing batch saved: {len(out)} rows -> {output_path}")
    return output_path


if __name__ == "__main__":
    run_simulate_missing()
