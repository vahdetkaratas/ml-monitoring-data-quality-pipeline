"""
Tests for simulation: reference dataset and batch generators. MILESTONES M1.
"""
import pandas as pd
import pytest

from src.simulation.build_reference_dataset import build_reference_dataset
from src.simulation.simulate_missing_batch import simulate_missing_batch
from src.simulation.simulate_numeric_drift_batch import simulate_numeric_drift_batch
from src.simulation.simulate_categorical_shift_batch import simulate_categorical_shift_batch
from src.simulation.simulate_prediction_shift_batch import simulate_prediction_shift_batch


def test_build_reference_dataset_shape_and_columns():
    df = build_reference_dataset(n_rows=100)
    assert len(df) == 100
    for col in ["customer_id", "tenure", "monthly_charges", "contract", "churn_score", "predicted_label"]:
        assert col in df.columns


def test_build_reference_dataset_ranges():
    df = build_reference_dataset(n_rows=200)
    assert df["tenure"].min() >= 0
    assert df["tenure"].max() <= 120
    assert df["churn_score"].min() >= 0
    assert df["churn_score"].max() <= 1
    assert set(df["predicted_label"].unique()).issubset({0, 1})


def test_simulate_missing_batch_adds_nans():
    ref = build_reference_dataset(n_rows=100)
    out = simulate_missing_batch(ref, missing_frac=0.2)
    assert out["monthly_charges"].isna().sum() >= 0
    assert out["total_charges"].isna().sum() >= 0


def test_simulate_numeric_drift_batch():
    ref = build_reference_dataset(n_rows=100)
    out = simulate_numeric_drift_batch(ref)
    assert "monthly_charges" in out.columns
    assert "tenure" in out.columns
    assert len(out) == len(ref)


def test_simulate_categorical_shift_batch():
    ref = build_reference_dataset(n_rows=100)
    out = simulate_categorical_shift_batch(ref)
    assert set(out["contract"].unique()).issubset({"Month-to-month", "One year", "Two year"})


def test_simulate_prediction_shift_batch():
    ref = build_reference_dataset(n_rows=100)
    out = simulate_prediction_shift_batch(ref)
    assert out["churn_score"].min() >= 0
    assert out["churn_score"].max() <= 1
    assert set(out["predicted_label"].unique()).issubset({0, 1})
