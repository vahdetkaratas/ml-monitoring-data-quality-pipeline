"""Tests for decision_summary layer."""
from src.reporting.decision_summary import build_decision_summary
from src.reporting.severity import CRITICAL, WARNING


def test_no_alerts_ok():
    d = build_decision_summary("ok", [])
    assert d["system_status"] == "OK"
    assert d["primary_issues"] == []
    assert len(d["recommended_actions"]) == 1
    assert "No alerts" in d["recommended_actions"][0]
    assert d["severity_overview"]["highest_alert_severity"] == "OK"
    assert d["severity_overview"]["counts"]["CRITICAL"] == 0


def test_critical_status_and_issues_ordered():
    alerts = [
        {"type": "drift", "severity": WARNING, "message": "Medium drift"},
        {"type": "validation", "severity": CRITICAL, "message": "Missing columns"},
    ]
    d = build_decision_summary("critical", alerts)
    assert d["system_status"] == "CRITICAL"
    assert d["primary_issues"][0].startswith("[CRITICAL]")
    assert "Missing columns" in d["primary_issues"][0]
    assert d["primary_issues"][1].startswith("[WARNING]")
    assert d["severity_overview"]["highest_alert_severity"] == CRITICAL
    assert any("Stop promotion" in a for a in d["recommended_actions"])


def test_actions_deduped_same_type():
    alerts = [
        {"type": "drift", "severity": CRITICAL, "message": "A"},
        {"type": "drift", "severity": CRITICAL, "message": "B"},
    ]
    d = build_decision_summary("critical", alerts)
    assert len(d["primary_issues"]) == 2
    # Same (type, severity) → one action string, deduplicated
    assert len(d["recommended_actions"]) == 1


def test_legacy_lowercase_severity_still_sorts():
    alerts = [
        {"type": "drift", "severity": "warning", "message": "W"},
        {"type": "validation", "severity": "critical", "message": "C"},
    ]
    d = build_decision_summary("warning", alerts)
    assert d["primary_issues"][0].startswith("[CRITICAL]")
