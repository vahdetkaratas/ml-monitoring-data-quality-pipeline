"""Tests for validation layer. MILESTONES M2."""
import pandas as pd
import pytest

from src.validation.schema_checks import check_required_columns, check_unknown_columns, check_column_dtypes
from src.validation.missing_checks import check_missing_rates
from src.validation.range_checks import check_ranges
from src.validation.categorical_checks import check_categorical
from src.pipeline.validation_pipeline import run_validation


@pytest.fixture
def schema():
    return {
        "customer_id": {"dtype": "string", "required": True},
        "tenure": {"dtype": "int", "required": True, "min": 0, "max": 120},
        "monthly_charges": {"dtype": "float", "required": True, "min": 0, "max": 500},
        "contract": {"dtype": "category", "required": True, "allowed_values": ["Month-to-month", "One year", "Two year"]},
    }


@pytest.fixture
def valid_df():
    return pd.DataFrame({
        "customer_id": ["a", "b"],
        "tenure": [10, 20],
        "monthly_charges": [50.0, 60.0],
        "contract": ["Month-to-month", "One year"],
    })


def test_check_required_columns_missing(schema, valid_df):
    df = valid_df.drop(columns=["tenure"])
    r = check_required_columns(df, schema)
    assert r["ok"] == False
    assert "tenure" in r["missing"]


def test_check_required_columns_ok(schema, valid_df):
    r = check_required_columns(valid_df, schema)
    assert r["ok"] == True


def test_check_missing_rates_ok(schema, valid_df):
    r = check_missing_rates(valid_df, schema, threshold=0.10)
    assert r["ok"] == True


def test_check_missing_rates_above(schema):
    df = pd.DataFrame({
        "customer_id": ["a"] * 10,
        "tenure": [1] * 10,
        "monthly_charges": [50.0] * 3 + [float("nan")] * 7,
        "contract": ["Month-to-month"] * 10,
    })
    r = check_missing_rates(df, schema, threshold=0.10)
    assert r["ok"] == False
    assert "monthly_charges" in r["columns_above_threshold"]


def test_check_ranges_ok(schema, valid_df):
    r = check_ranges(valid_df, schema)
    assert r["ok"] == True


def test_check_ranges_max_violation_even_if_min_ok(schema):
    """Regression: max must be evaluated even when min is satisfied."""
    df = pd.DataFrame({
        "customer_id": ["a"],
        "tenure": [10],
        "monthly_charges": [600.0],
        "contract": ["Month-to-month"],
    })
    r = check_ranges(df, schema)
    assert r["ok"] is False
    assert "monthly_charges" in r["out_of_range_columns"]


def test_check_unknown_columns_ok(schema, valid_df):
    r = check_unknown_columns(valid_df, schema)
    assert r["ok"] is True
    assert r["unknown_columns"] == []


def test_check_unknown_columns_warns(schema, valid_df):
    df = valid_df.copy()
    df["extra_feature"] = [1, 2]
    r = check_unknown_columns(df, schema)
    assert r["ok"] is False
    assert "extra_feature" in r["unknown_columns"]


def test_check_categorical_invalid(schema):
    df = pd.DataFrame({
        "customer_id": ["a"],
        "tenure": [1],
        "monthly_charges": [50.0],
        "contract": ["Unknown"],
    })
    r = check_categorical(df, schema)
    assert r["ok"] == False
    assert "contract" in r["invalid_categories"]


def test_run_validation_ok(schema, valid_df):
    out = run_validation(valid_df, schema=schema)
    assert out["status"] in ("ok", "warning", "critical")
    assert "checks" in out
    assert out["status"] == "ok"


def test_run_validation_unknown_column_warning(schema, valid_df):
    df = valid_df.copy()
    df["extra_feature"] = [1, 2]
    out = run_validation(df, schema=schema)
    assert out["status"] == "warning"
    assert out["checks"]["unknown_columns"]["ok"] is False
