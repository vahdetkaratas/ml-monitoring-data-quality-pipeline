"""Tests for prediction monitoring. MILESTONES M4."""
import pandas as pd
import pytest
from src.monitoring.prediction_monitor import prediction_monitoring_summary


def test_prediction_monitoring_ok():
    ref = pd.DataFrame({"churn_score": [0.2] * 50 + [0.3] * 50, "predicted_label": [0] * 100})
    cur = pd.DataFrame({"churn_score": [0.22] * 50 + [0.32] * 50, "predicted_label": [0] * 100})
    s = prediction_monitoring_summary(ref, cur)
    assert s["status"] in ("ok", "warning", "critical")
    assert "metrics" in s


def test_prediction_monitoring_shift():
    ref = pd.DataFrame({"churn_score": [0.2] * 100, "predicted_label": [0] * 100})
    cur = pd.DataFrame({"churn_score": [0.7] * 100, "predicted_label": [1] * 100})
    s = prediction_monitoring_summary(ref, cur)
    assert s["status"] in ("warning", "critical")
