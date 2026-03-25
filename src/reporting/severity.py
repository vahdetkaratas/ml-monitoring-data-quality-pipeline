"""
Canonical alert severity labels and ordering. Used by alerts, decision summary, and Streamlit.
"""
from __future__ import annotations

from collections import Counter

CRITICAL = "CRITICAL"
WARNING = "WARNING"
INFO = "INFO"
OK = "OK"

# Sort: most urgent first (used for alerts and primary-issues ordering)
_RANK = {CRITICAL: 0, WARNING: 1, INFO: 2}
_DEFAULT_RANK = 9


def normalize_severity(value: str | None) -> str:
    """Map legacy lowercase or unknown input to CRITICAL / WARNING / INFO."""
    if value is None or not str(value).strip():
        return WARNING
    u = str(value).strip().upper()
    if u in (CRITICAL, WARNING, INFO):
        return u
    return WARNING


def severity_rank(severity: str) -> int:
    return _RANK.get(normalize_severity(severity), _DEFAULT_RANK)


def highest_alert_severity(alerts: list[dict]) -> str:
    """Worst severity among alerts, or OK if there are none."""
    if not alerts:
        return OK
    best = min(severity_rank(a.get("severity")) for a in alerts)
    for label, r in _RANK.items():
        if r == best:
            return label
    return INFO


def severity_counts(alerts: list[dict]) -> dict[str, int]:
    c = Counter(normalize_severity(a.get("severity")) for a in alerts if a.get("severity"))
    return {CRITICAL: c.get(CRITICAL, 0), WARNING: c.get(WARNING, 0), INFO: c.get(INFO, 0)}


def build_severity_overview(alerts: list[dict]) -> dict:
    counts = severity_counts(alerts)
    highest = highest_alert_severity(alerts)
    return {
        "highest_alert_severity": highest,
        "counts": counts,
        "attention_priority": (
            "Address CRITICAL alerts first (block or escalate), then WARNING (triage and fix). "
            "INFO is contextual only unless your runbook says otherwise."
        ),
    }
