"""
Repository-root paths. All artifact and sample data locations resolve from here so
pipeline, Streamlit, and CLI work regardless of process cwd (as long as ``src`` is importable).
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SCHEMA_PATH = REPO_ROOT / "data" / "metadata" / "schema_definition.json"
REFERENCE_DATASET_CSV = REPO_ROOT / "data" / "reference" / "reference_dataset.csv"
DATA_CURRENT_DIR = REPO_ROOT / "data" / "current"

ARTIFACTS_REPORTS_DIR = REPO_ROOT / "artifacts" / "reports"
ARTIFACTS_DRIFT_DIR = REPO_ROOT / "artifacts" / "drift"
ARTIFACTS_VALIDATION_DIR = REPO_ROOT / "artifacts" / "validation"
