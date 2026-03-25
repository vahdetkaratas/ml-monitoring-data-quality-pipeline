"""Export report JSON and monitoring_overview.csv. IMPLEMENTATION_REFERENCE §11."""
from pathlib import Path
import json
import pandas as pd
from src.utils.file_helpers import ensure_dir
from src.utils.paths import ARTIFACTS_REPORTS_DIR

OUTPUT_REPORTS = ARTIFACTS_REPORTS_DIR


def export_report(report: dict, output_dir: str | Path | None = None) -> Path:
    """Write report as JSON. Returns path."""
    output_dir = Path(output_dir or OUTPUT_REPORTS)
    ensure_dir(output_dir)
    path = output_dir / f"report_{Path(report['batch_name']).stem}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return path


def export_overview_csv(rows: list[dict], output_path: str | Path | None = None) -> Path:
    """Append or write monitoring_overview.csv. Columns: batch_name, overall_status, validation_status, drift_status, prediction_monitoring_status, alert_count."""
    output_path = Path(output_path or OUTPUT_REPORTS / "monitoring_overview.csv")
    ensure_dir(output_path.parent)
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    return output_path
