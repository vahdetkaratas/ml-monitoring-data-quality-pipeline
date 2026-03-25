"""Tests for alert rule outputs."""
from src.reporting.alert_rules import alerts_from_prediction
from src.reporting.severity import CRITICAL, INFO, WARNING


def test_prediction_info_when_no_churn_score():
    pred = {"status": "ok", "message": "No churn_score column", "metrics": {}}
    alerts = alerts_from_prediction(pred)
    assert len(alerts) == 1
    assert alerts[0]["severity"] == INFO
    assert alerts[0]["type"] == "prediction_monitoring"


def test_prediction_critical_uses_uppercase():
    pred = {"status": "critical", "metrics": {}}
    alerts = alerts_from_prediction(pred)
    assert alerts[0]["severity"] == CRITICAL


def test_prediction_warning_uses_uppercase():
    pred = {"status": "warning", "metrics": {}}
    alerts = alerts_from_prediction(pred)
    assert alerts[0]["severity"] == WARNING


def test_prediction_ok_with_scores_no_extra_info_alert():
    pred = {
        "status": "ok",
        "metrics": {"score_psi": 0.01},
    }
    assert alerts_from_prediction(pred) == []
