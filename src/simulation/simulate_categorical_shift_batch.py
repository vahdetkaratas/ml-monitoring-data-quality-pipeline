"""
Simulate current batch with categorical shift (contract proportions changed). MONITORING_SYSTEM_DESIGN §2, MILESTONES M1.
"""
from pathlib import Path
import numpy as np
import pandas as pd

from src.utils.paths import DATA_CURRENT_DIR, REFERENCE_DATASET_CSV

CURRENT_DIR = DATA_CURRENT_DIR


def simulate_categorical_shift_batch(reference_df: pd.DataFrame, seed: int = 47) -> pd.DataFrame:
    """Change contract (and optionally internet_service) proportions to trigger categorical drift."""
    rng = np.random.default_rng(seed)
    df = reference_df.copy()
    if "contract" in df.columns:
        # Shift: more Month-to-month, fewer Two year
        df["contract"] = rng.choice(
            ["Month-to-month", "One year", "Two year"],
            p=[0.75, 0.2, 0.05],
            size=len(df),
        )
    if "internet_service" in df.columns:
        df["internet_service"] = rng.choice(
            ["DSL", "Fiber optic", "No"],
            p=[0.25, 0.6, 0.15],
            size=len(df),
        )
    return df


def run_simulate_categorical_shift(
    reference_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> Path:
    ref_path = Path(reference_path or REFERENCE_DATASET_CSV)
    if not ref_path.exists():
        raise FileNotFoundError(f"Reference not found: {ref_path}.")
    ref = pd.read_csv(ref_path)
    ref_sample = ref.sample(n=min(500, len(ref)), random_state=48).reset_index(drop=True)
    out = simulate_categorical_shift_batch(ref_sample)
    output_path = Path(output_path or CURRENT_DIR / "current_batch_categorical_shift.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    print(f"Categorical shift batch saved: {len(out)} rows -> {output_path}")
    return output_path


if __name__ == "__main__":
    run_simulate_categorical_shift()
