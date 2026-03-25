"""Tests for drift detection. MILESTONES M3."""
import pandas as pd
import pytest
from src.drift.psi import psi_numeric, psi_categorical
from src.drift.numeric_drift import numeric_drift_metric
from src.drift.categorical_drift import categorical_drift_metric
from src.drift.drift_summary import compute_drift_summary


def test_psi_numeric_same():
    ref = pd.Series([1.0, 2.0, 3.0] * 10)
    cur = pd.Series([1.0, 2.0, 3.0] * 10)
    assert psi_numeric(ref, cur) < 0.1


def test_psi_categorical():
    ref = pd.Series(["A", "B", "C"] * 10)
    cur = pd.Series(["A", "B", "C"] * 10)
    assert psi_categorical(ref, cur) < 0.1


def test_numeric_drift_metric():
    ref = pd.Series([10.0] * 50 + [20.0] * 50)
    cur = pd.Series([30.0] * 50 + [40.0] * 50)
    m = numeric_drift_metric(ref, cur)
    assert "psi" in m
    assert "severity" in m


def test_drift_summary():
    ref = pd.DataFrame({"tenure": [1, 2, 3] * 30, "monthly_charges": [50.0] * 90, "contract": ["Month-to-month"] * 90})
    cur = pd.DataFrame({"tenure": [10, 20, 30] * 30, "monthly_charges": [80.0] * 90, "contract": ["One year"] * 90})
    s = compute_drift_summary(ref, cur)
    assert "status" in s
    assert "high_count" in s
    assert "per_column" in s
