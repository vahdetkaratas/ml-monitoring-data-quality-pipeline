"""
Simulate current batch with prediction shift (churn_score and positive rate shifted). MONITORING_SYSTEM_DESIGN §2, MILESTONES M1.
"""
from pathlib import Path
import numpy as np
import pandas as pd

from src.utils.paths import DATA_CURRENT_DIR, REFERENCE_DATASET_CSV

CURRENT_DIR = DATA_CURRENT_DIR


def simulate_prediction_shift_batch(reference_df: pd.DataFrame, seed: int = 49) -> pd.DataFrame:
    """Shift churn_score distribution and positive rate to trigger prediction monitoring alarm."""
    rng = np.random.default_rng(seed)
    df = reference_df.copy()
    if "churn_score" in df.columns:
        # Shift scores upward (higher churn rate)
        df["churn_score"] = np.clip(df["churn_score"] * 1.4 + rng.normal(0.1, 0.05, len(df)), 0, 1)
    if "predicted_label" in df.columns:
        df["predicted_label"] = (df["churn_score"] >= 0.5).astype(int)
    return df


def run_simulate_prediction_shift(
    reference_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> Path:
    ref_path = Path(reference_path or REFERENCE_DATASET_CSV)
    if not ref_path.exists():
        raise FileNotFoundError(f"Reference not found: {ref_path}.")
    ref = pd.read_csv(ref_path)
    ref_sample = ref.sample(n=min(500, len(ref)), random_state=50).reset_index(drop=True)
    out = simulate_prediction_shift_batch(ref_sample)
    output_path = Path(output_path or CURRENT_DIR / "current_batch_prediction_shift.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    print(f"Prediction shift batch saved: {len(out)} rows -> {output_path}")
    return output_path


if __name__ == "__main__":
    run_simulate_prediction_shift()
