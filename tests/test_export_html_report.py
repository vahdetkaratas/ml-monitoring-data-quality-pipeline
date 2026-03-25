"""Tests for static HTML run export."""

from src.reporting.export_html_report import export_run_html_report, render_run_html


def _minimal_report(batch: str = "current_batch_clean.csv") -> dict:
    return {
        "batch_name": batch,
        "overall_status": "ok",
        "summary": {
            "validation_status": "ok",
            "drift_status": "ok",
            "prediction_monitoring_status": "ok",
        },
        "alert_count": 0,
        "alerts": [],
        "decision_summary": {
            "system_status": "OK",
            "severity_overview": {
                "highest_alert_severity": "OK",
                "counts": {"CRITICAL": 0, "WARNING": 0, "INFO": 0},
                "attention_priority": "Test attention text.",
            },
            "primary_issues": [],
            "recommended_actions": ["Continue monitoring."],
        },
        "run_metadata": {
            "run_id": "test-run-id",
            "generated_at": "2025-01-01T00:00:00+00:00",
            "n_batches": 1,
            "batch_index": 1,
            "schema_version": "1.0",
            "pipeline_version": "9.9.9",
            "reference_dataset": "data/reference/ref.csv",
            "current_batch_file": f"data/current/{batch}",
        },
    }


def test_render_run_html_contains_sections():
    html_out = render_run_html([_minimal_report()])
    assert "<!DOCTYPE html>" in html_out
    assert "Run metadata" in html_out
    assert "Run overview" in html_out
    assert "Severity overview" in html_out
    assert "Decision summary" in html_out
    assert "Layer status" in html_out
    assert "current_batch_clean.csv" in html_out
    assert "test-run-id" in html_out


def test_render_escapes_angle_brackets():
    rep = _minimal_report()
    rep["alerts"] = [{"severity": "WARNING", "type": "validation", "message": "Use <script>"}]
    html_out = render_run_html([rep])
    assert "<script>" not in html_out
    assert "&lt;script&gt;" in html_out


def test_export_empty_returns_none():
    assert export_run_html_report([]) is None


def test_export_writes_file(tmp_path):
    p = tmp_path / "out.html"
    out = export_run_html_report([_minimal_report()], output_path=p)
    assert out == p
    assert p.exists()
    assert p.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")
