"""Alert rules: map validation/drift/prediction status to severity. MONITORING_SYSTEM_DESIGN §6."""
from src.reporting.severity import CRITICAL, INFO, WARNING


def alerts_from_validation(validation_summary: dict) -> list[dict]:
    """Build alert list from validation result."""
    alerts = []
    if not validation_summary.get("checks"):
        return alerts
    c = validation_summary["checks"]
    if not c.get("required_columns", {}).get("ok"):
        alerts.append(
            {
                "type": "validation",
                "severity": CRITICAL,
                "message": f"Missing columns: {c['required_columns'].get('missing', [])}",
            }
        )
    unk = c.get("unknown_columns")
    if unk and not unk.get("ok"):
        alerts.append(
            {
                "type": "validation",
                "severity": WARNING,
                "message": f"Unknown columns (not in schema): {unk.get('unknown_columns', [])}",
            }
        )
    if not c.get("dtypes", {}).get("ok"):
        alerts.append(
            {
                "type": "validation",
                "severity": CRITICAL,
                "message": f"Dtype issues: {c['dtypes'].get('issues', [])}",
            }
        )
    if not c.get("missing", {}).get("ok"):
        alerts.append(
            {
                "type": "validation",
                "severity": WARNING,
                "message": f"Missing above threshold: {c['missing'].get('columns_above_threshold', [])}",
            }
        )
    if not c.get("ranges", {}).get("ok"):
        alerts.append(
            {
                "type": "validation",
                "severity": WARNING,
                "message": f"Out of range: {c['ranges'].get('out_of_range_columns', [])}",
            }
        )
    if not c.get("categorical", {}).get("ok"):
        alerts.append(
            {
                "type": "validation",
                "severity": WARNING,
                "message": f"Invalid categories: {c['categorical'].get('invalid_categories', {})}",
            }
        )
    return alerts


def alerts_from_drift(drift_summary: dict) -> list[dict]:
    """Build alert list from drift result."""
    alerts = []
    if drift_summary.get("high_count", 0) > 0:
        alerts.append(
            {
                "type": "drift",
                "severity": CRITICAL,
                "message": f"High drift count: {drift_summary['high_count']}",
            }
        )
    if drift_summary.get("medium_count", 0) > 0:
        alerts.append(
            {
                "type": "drift",
                "severity": WARNING,
                "message": f"Medium drift count: {drift_summary['medium_count']}",
            }
        )
    return alerts


def alerts_from_prediction(pred_summary: dict) -> list[dict]:
    """Build alert list from prediction monitoring result."""
    alerts = []
    if pred_summary.get("status") == "critical":
        alerts.append(
            {
                "type": "prediction_monitoring",
                "severity": CRITICAL,
                "message": "Score or positive rate shift critical",
            }
        )
    elif pred_summary.get("status") == "warning":
        alerts.append(
            {
                "type": "prediction_monitoring",
                "severity": WARNING,
                "message": "Score or positive rate shift warning",
            }
        )
    elif pred_summary.get("message") == "No churn_score column":
        alerts.append(
            {
                "type": "prediction_monitoring",
                "severity": INFO,
                "message": pred_summary["message"],
            }
        )
    return alerts
