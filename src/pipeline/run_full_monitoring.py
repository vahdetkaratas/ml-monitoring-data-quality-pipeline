"""
Full monitoring pipeline: validation + drift + prediction + report for each current batch. MILESTONES M5.
"""
from pathlib import Path
import json
import uuid
from datetime import datetime, timezone
import pandas as pd
from src.pipeline.validation_pipeline import run_validation
from src.validation.load_schema import load_schema
from src.drift.drift_summary import compute_drift_summary
from src.monitoring.prediction_monitor import prediction_monitoring_summary
from src.reporting.build_report import build_report
from src.reporting.export_results import export_report, export_overview_csv
from src.reporting.export_html_report import export_run_html_report
from src.reporting.run_metadata import build_run_metadata
from src.utils.file_helpers import ensure_dir
from src.utils.paths import (
    REFERENCE_DATASET_CSV,
    DATA_CURRENT_DIR,
    ARTIFACTS_REPORTS_DIR,
    ARTIFACTS_DRIFT_DIR,
)

REFERENCE_PATH = REFERENCE_DATASET_CSV
CURRENT_DIR = DATA_CURRENT_DIR
OUTPUT_REPORTS = ARTIFACTS_REPORTS_DIR
OUTPUT_DRIFT = ARTIFACTS_DRIFT_DIR


def run_monitoring_for_batch(
    current_path: Path,
    reference_df: pd.DataFrame,
    schema: dict,
    run_metadata: dict,
) -> dict:
    """Run validation, drift, prediction; save drift to artifacts/drift; return final report dict."""
    current_df = pd.read_csv(current_path)
    validation_summary = run_validation(current_df, schema=schema)
    drift_summary = compute_drift_summary(reference_df, current_df)
    prediction_summary = prediction_monitoring_summary(reference_df, current_df)
    ensure_dir(OUTPUT_DRIFT)
    drift_path = OUTPUT_DRIFT / f"drift_{current_path.stem}.json"
    with open(drift_path, "w", encoding="utf-8") as f:
        json.dump(drift_summary, f, indent=2)
    report = build_report(
        batch_name=current_path.name,
        validation_summary=validation_summary,
        drift_summary=drift_summary,
        prediction_summary=prediction_summary,
        run_metadata=run_metadata,
    )
    return report


def run_full_monitoring(
    reference_path: str | Path | None = None,
    current_dir: str | Path | None = None,
) -> list[dict]:
    """Run monitoring for all current batches; export reports and overview CSV. Returns list of reports."""
    reference_path = Path(reference_path or REFERENCE_PATH)
    current_dir = Path(current_dir or CURRENT_DIR)
    if not reference_path.exists():
        raise FileNotFoundError(f"Reference not found: {reference_path}. Run simulation first.")
    reference_df = pd.read_csv(reference_path)
    schema, schema_file_meta = load_schema()
    batch_paths = sorted(current_dir.glob("current_batch_*.csv"))
    n_batches = len(batch_paths)
    run_id = str(uuid.uuid4())
    schema_version = schema_file_meta.get("schema_version")
    if schema_version is not None:
        schema_version = str(schema_version)

    reports = []
    for batch_index, path in enumerate(batch_paths, start=1):
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        run_metadata = build_run_metadata(
            run_id=run_id,
            generated_at=generated_at,
            n_batches=n_batches,
            batch_index=batch_index,
            schema_version=schema_version,
            reference_dataset=reference_path,
            current_batch_file=path,
        )
        report = run_monitoring_for_batch(path, reference_df, schema, run_metadata)
        reports.append(report)
        export_report(report)
    overview_rows = [
        {
            "batch_name": r["batch_name"],
            "overall_status": r["overall_status"],
            "validation_status": r["summary"]["validation_status"],
            "drift_status": r["summary"]["drift_status"],
            "prediction_monitoring_status": r["summary"]["prediction_monitoring_status"],
            "alert_count": r["alert_count"],
        }
        for r in reports
    ]
    export_overview_csv(overview_rows)
    html_path = export_run_html_report(reports)
    print(f"Monitoring done: {len(reports)} batches -> {OUTPUT_REPORTS}")
    if html_path:
        print(f"HTML run report -> {html_path}")
    return reports


if __name__ == "__main__":
    run_full_monitoring()
