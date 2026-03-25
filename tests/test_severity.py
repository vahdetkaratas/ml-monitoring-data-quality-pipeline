"""Tests for canonical severity helpers."""
from src.reporting.severity import (
    CRITICAL,
    INFO,
    OK,
    WARNING,
    build_severity_overview,
    highest_alert_severity,
    normalize_severity,
)


def test_normalize_legacy_lowercase():
    assert normalize_severity("critical") == CRITICAL
    assert normalize_severity("warning") == WARNING


def test_highest_severity_worst_wins():
    alerts = [
        {"severity": WARNING, "message": "w"},
        {"severity": CRITICAL, "message": "c"},
    ]
    assert highest_alert_severity(alerts) == CRITICAL


def test_highest_ok_when_empty():
    assert highest_alert_severity([]) == OK


def test_overview_counts():
    o = build_severity_overview(
        [
            {"severity": CRITICAL},
            {"severity": WARNING},
            {"severity": WARNING},
            {"severity": INFO},
        ]
    )
    assert o["highest_alert_severity"] == CRITICAL
    assert o["counts"][CRITICAL] == 1
    assert o["counts"][WARNING] == 2
    assert o["counts"][INFO] == 1
    assert "attention_priority" in o
