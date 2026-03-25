"""Tests for run metadata and schema file meta loading."""
import json
from pathlib import Path

import pytest

from src.reporting.run_metadata import PIPELINE_VERSION, build_run_metadata
from src.utils.paths import REPO_ROOT
from src.validation.load_schema import load_schema


def test_build_run_metadata_paths_relative_to_repo(tmp_path, monkeypatch):
    ref = tmp_path / "ref.csv"
    cur = tmp_path / "cur.csv"
    ref.write_text("a")
    cur.write_text("b")
    monkeypatch.setattr("src.reporting.run_metadata.REPO_ROOT", tmp_path)
    meta = build_run_metadata(
        run_id="rid",
        generated_at="2025-01-01T00:00:00+00:00",
        n_batches=3,
        batch_index=2,
        schema_version="1.0",
        reference_dataset=ref,
        current_batch_file=cur,
    )
    assert meta["run_id"] == "rid"
    assert meta["n_batches"] == 3
    assert meta["batch_index"] == 2
    assert meta["schema_version"] == "1.0"
    assert meta["pipeline_version"] == PIPELINE_VERSION
    assert meta["reference_dataset"] == "ref.csv"
    assert meta["current_batch_file"] == "cur.csv"


def test_load_schema_strips_meta_and_returns_version():
    schema, file_meta = load_schema(REPO_ROOT / "data" / "metadata" / "schema_definition.json")
    assert "__meta__" not in schema
    assert "customer_id" in schema
    assert file_meta.get("schema_version") == "1.0"


def test_load_schema_missing_file():
    schema, file_meta = load_schema(Path("/nonexistent/schema_xyz.json"))
    assert schema == {}
    assert file_meta == {}


def test_load_schema_temp_with_meta(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(
        json.dumps(
            {
                "__meta__": {"schema_version": "test-2"},
                "col_a": {"dtype": "int", "required": True},
            }
        ),
        encoding="utf-8",
    )
    schema, file_meta = load_schema(p)
    assert schema == {"col_a": {"dtype": "int", "required": True}}
    assert file_meta == {"schema_version": "test-2"}
