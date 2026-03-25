"""Build final report: overall_status, summary, alerts, decision_summary. MONITORING_SYSTEM_DESIGN §8."""
from src.reporting.alert_rules import alerts_from_validation, alerts_from_drift, alerts_from_prediction
from src.reporting.aggregate_summary import aggregate_summary
from src.reporting.decision_summary import build_decision_summary


def build_report(
    batch_name: str,
    validation_summary: dict,
    drift_summary: dict,
    prediction_summary: dict,
    run_metadata: dict | None = None,
) -> dict:
    """Assemble final report JSON; birleştirme aggregate_summary ile yapılır."""
    agg = aggregate_summary(validation_summary, drift_summary, prediction_summary)
    alerts = []
    alerts.extend(alerts_from_validation(validation_summary))
    alerts.extend(alerts_from_drift(drift_summary))
    alerts.extend(alerts_from_prediction(prediction_summary))
    decision_summary = build_decision_summary(agg["overall_status"], alerts)
    return {
        "batch_name": batch_name,
        "overall_status": agg["overall_status"],
        "summary": agg["summary"],
        "alert_count": len(alerts),
        "alerts": alerts,
        "decision_summary": decision_summary,
        "run_metadata": run_metadata if run_metadata is not None else {},
    }
