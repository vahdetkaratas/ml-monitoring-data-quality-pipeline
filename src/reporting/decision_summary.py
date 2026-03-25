"""
Decision-oriented summary derived from aggregate status and existing alerts only.
No separate rule engine: issues and actions are explainable from validation / drift / prediction alerts.
"""
from __future__ import annotations

from src.reporting.severity import (
    CRITICAL,
    INFO,
    WARNING,
    build_severity_overview,
    normalize_severity,
    severity_rank,
)

_STATUS_TO_SYSTEM = {"ok": "OK", "warning": "WARNING", "critical": "CRITICAL"}


def _sort_alerts(alerts: list[dict]) -> list[dict]:
    return sorted(alerts, key=lambda a: severity_rank(a.get("severity")))


def _action_for(alert: dict) -> str:
    """One practical next step per alert type + severity (portfolio-friendly, fixed mapping)."""
    t = alert.get("type")
    s = normalize_severity(alert.get("severity"))
    if t == "validation" and s == CRITICAL:
        return (
            "Stop promotion of this batch: work with the data producer to restore required columns "
            "and fix dtype failures, then re-run validation."
        )
    if t == "validation" and s == WARNING:
        return (
            "Triage validation warnings with domain owners (missing rates, ranges, categories, "
            "or unknown columns) and update the schema or pipeline as needed."
        )
    if t == "drift" and s == CRITICAL:
        return (
            "Investigate high-drift features vs the reference window: check definitions, ingestion, "
            "and whether the cohort mix changed materially."
        )
    if t == "drift" and s == WARNING:
        return (
            "Monitor medium-drift features on the next batches; document whether the shift is expected "
            "(e.g. campaign or product change)."
        )
    if t == "prediction_monitoring" and s == CRITICAL:
        return (
            "Review model calibration and business thresholds; plan validation, rollback, or refresh "
            "if score or positive-rate shift persists."
        )
    if t == "prediction_monitoring" and s == WARNING:
        return (
            "Watch score and positive-rate trends on upcoming batches; correlate with known operational changes."
        )
    if t == "prediction_monitoring" and s == INFO:
        return (
            "If scores should be monitored, ensure `churn_score` is present in both reference and current "
            "data; otherwise document that prediction monitoring is intentionally out of scope."
        )
    return "Review the full report, drift table, and batch CSV for details."


def build_decision_summary(overall_status: str, alerts: list[dict]) -> dict:
    """
    Returns:
        system_status: OK | WARNING | CRITICAL (from overall_status)
        severity_overview: counts, highest_alert_severity, attention_priority text
        primary_issues: up to 5 lines, CRITICAL first, prefixed with severity label
        recommended_actions: up to 5 deduplicated actions derived from those alerts
    """
    system_status = _STATUS_TO_SYSTEM.get(overall_status, str(overall_status).upper())
    ordered = _sort_alerts(list(alerts))
    primary_issues = [
        f"[{normalize_severity(a.get('severity'))}] {a.get('message', '')}".strip()
        for a in ordered[:5]
        if a.get("message")
    ]

    seen: set[str] = set()
    recommended_actions: list[str] = []
    for a in ordered:
        act = _action_for(a)
        if act not in seen:
            seen.add(act)
            recommended_actions.append(act)
        if len(recommended_actions) >= 5:
            break

    if not alerts:
        primary_issues = []
        recommended_actions = [
            "No alerts fired for this batch under current thresholds; continue routine monitoring."
        ]

    severity_overview = build_severity_overview(alerts)

    return {
        "system_status": system_status,
        "severity_overview": severity_overview,
        "primary_issues": primary_issues,
        "recommended_actions": recommended_actions,
    }
