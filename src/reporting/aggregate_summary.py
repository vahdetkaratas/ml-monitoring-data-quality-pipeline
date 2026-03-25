"""Aggregate validation, drift, and prediction layer statuses into one overall status. See MONITORING_SYSTEM_DESIGN §7."""


def overall_status(validation_status: str, drift_status: str, prediction_status: str) -> str:
    """critical > warning > ok (MONITORING_SYSTEM_DESIGN §7)."""
    for s in (validation_status, drift_status, prediction_status):
        if s == "critical":
            return "critical"
    for s in (validation_status, drift_status, prediction_status):
        if s == "warning":
            return "warning"
    return "ok"


def aggregate_summary(
    validation_summary: dict,
    drift_summary: dict,
    prediction_summary: dict,
) -> dict:
    """Return overall_status plus per-layer statuses for the report summary block."""
    v_status = validation_summary.get("status", "ok")
    d_status = drift_summary.get("status", "ok")
    p_status = prediction_summary.get("status", "ok")
    return {
        "overall_status": overall_status(v_status, d_status, p_status),
        "summary": {
            "validation_status": v_status,
            "drift_status": d_status,
            "prediction_monitoring_status": p_status,
        },
    }
