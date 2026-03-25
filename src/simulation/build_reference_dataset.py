"""
Build reference dataset: Churn-style synthetic "normal" data. MONITORING_SYSTEM_DESIGN §2, MILESTONES M1.
Columns: customer_id, tenure, monthly_charges, total_charges, contract, internet_service, payment_method,
         num_active_services, senior_citizen, churn_score, predicted_label.
"""
from pathlib import Path
import numpy as np
import pandas as pd

from src.utils.paths import REFERENCE_DATASET_CSV

REFERENCE_PATH = REFERENCE_DATASET_CSV
DEFAULT_N_ROWS = 3000


def build_reference_dataset(n_rows: int = DEFAULT_N_ROWS, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic reference dataset with Churn-style schema."""
    rng = np.random.default_rng(seed)
    n = n_rows

    df = pd.DataFrame({
        "customer_id": [f"ref-{i}" for i in range(n)],
        "tenure": rng.integers(0, 73, size=n),
        "monthly_charges": np.clip(rng.lognormal(4.0, 0.6, n), 18, 118),
        "total_charges": np.clip(rng.lognormal(6.5, 1.0, n), 0, 8500),
        "contract": rng.choice(["Month-to-month", "One year", "Two year"], p=[0.5, 0.3, 0.2], size=n),
        "internet_service": rng.choice(["DSL", "Fiber optic", "No"], p=[0.35, 0.45, 0.2], size=n),
        "payment_method": rng.choice(
            ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
            size=n,
        ),
        "num_active_services": rng.integers(0, 9, size=n),
        "senior_citizen": rng.integers(0, 2, size=n),
    })
    # churn_score: beta-like, mean ~0.27
    df["churn_score"] = np.clip(rng.beta(2, 5, n), 0, 1)
    df["predicted_label"] = (df["churn_score"] >= 0.5).astype(int)
    return df


def run_build_reference(output_path: str | Path | None = None, n_rows: int = DEFAULT_N_ROWS) -> Path:
    """Build and save reference dataset. Returns path to CSV."""
    from src.utils.file_helpers import ensure_dir
    output_path = Path(output_path or REFERENCE_DATASET_CSV)
    ensure_dir(output_path.parent)
    df = build_reference_dataset(n_rows=n_rows)
    df.to_csv(output_path, index=False)
    print(f"Reference dataset saved: {len(df)} rows -> {output_path}")
    return output_path


if __name__ == "__main__":
    run_build_reference()
