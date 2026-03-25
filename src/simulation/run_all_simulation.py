"""
Run all simulation steps: reference + 5 current batches. MILESTONES M1.
"""
from pathlib import Path

from src.utils.paths import DATA_CURRENT_DIR, REFERENCE_DATASET_CSV
from src.simulation.build_reference_dataset import run_build_reference
from src.simulation.simulate_missing_batch import run_simulate_missing
from src.simulation.simulate_numeric_drift_batch import run_simulate_numeric_drift
from src.simulation.simulate_categorical_shift_batch import run_simulate_categorical_shift
from src.simulation.simulate_prediction_shift_batch import run_simulate_prediction_shift

CURRENT_DIR = DATA_CURRENT_DIR


def run_clean_batch(reference_path: Path, output_path: Path) -> Path:
    """Save a sample of reference as current_batch_clean.csv."""
    import pandas as pd
    ref = pd.read_csv(reference_path)
    sample = ref.sample(n=min(500, len(ref)), random_state=41).reset_index(drop=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(output_path, index=False)
    print(f"Clean batch saved: {len(sample)} rows -> {output_path}")
    return output_path


def run_all_simulation(
    reference_path: str | Path | None = None,
    current_dir: str | Path | None = None,
    n_reference: int = 3000,
) -> None:
    """Build reference dataset and all 5 current batches."""
    ref_path = Path(reference_path or REFERENCE_DATASET_CSV)
    current_dir = Path(current_dir or CURRENT_DIR)
    run_build_reference(output_path=ref_path, n_rows=n_reference)
    run_clean_batch(ref_path, current_dir / "current_batch_clean.csv")
    run_simulate_missing(reference_path=ref_path, output_path=current_dir / "current_batch_missing.csv")
    run_simulate_numeric_drift(reference_path=ref_path, output_path=current_dir / "current_batch_numeric_drift.csv")
    run_simulate_categorical_shift(reference_path=ref_path, output_path=current_dir / "current_batch_categorical_shift.csv")
    run_simulate_prediction_shift(reference_path=ref_path, output_path=current_dir / "current_batch_prediction_shift.csv")
    print("All simulation done: reference + 5 current batches.")


if __name__ == "__main__":
    run_all_simulation()
