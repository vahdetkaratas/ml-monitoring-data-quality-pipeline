"""
Static HTML export for a full monitoring run (all batch reports).
Single file, no template engine: reads the same dicts written as JSON.
"""
from __future__ import annotations

import html
from pathlib import Path

from src.utils.file_helpers import ensure_dir
from src.utils.paths import ARTIFACTS_REPORTS_DIR

_RUN_META_KEYS = ("run_id", "n_batches", "schema_version", "pipeline_version", "reference_dataset")


def _e(value) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=False)


def _status_class(status: str) -> str:
    s = str(status).lower()
    if s == "critical":
        return "tag-critical"
    if s == "warning":
        return "tag-warning"
    return "tag-ok"


def _render_alerts_table(alerts: list[dict]) -> str:
    if not alerts:
        return "<p class='muted'>No alerts.</p>"
    rows = []
    for a in alerts:
        sev = _e(a.get("severity", ""))
        typ = _e(a.get("type", ""))
        msg = _e(a.get("message", ""))
        rows.append(f"<tr><td>{sev}</td><td>{typ}</td><td>{msg}</td></tr>")
    body = "".join(rows)
    return (
        "<table><thead><tr><th>Severity</th><th>Type</th><th>Message</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def _render_batch(report: dict) -> str:
    raw_batch = report.get("batch_name", "batch")
    slug = _e(Path(str(raw_batch)).stem.replace(" ", "-"))
    display = _e(raw_batch)
    overall = report.get("overall_status", "")
    summ = report.get("summary") or {}
    decision = report.get("decision_summary") or {}
    sov = decision.get("severity_overview") or {}
    counts = sov.get("counts") or {}
    issues = decision.get("primary_issues") or []
    actions = decision.get("recommended_actions") or []
    alerts = report.get("alerts") or []
    rm = report.get("run_metadata") or {}

    issues_html = "".join(f"<li>{_e(i)}</li>" for i in issues) or "<li class='muted'>None</li>"
    actions_html = "".join(f"<li>{_e(a)}</li>" for a in actions)

    crit = counts.get("CRITICAL", 0)
    warn = counts.get("WARNING", 0)
    info = counts.get("INFO", 0)
    highest = _e(sov.get("highest_alert_severity", "—"))
    attention = _e(sov.get("attention_priority", ""))

    v_status = _e(summ.get("validation_status", "—"))
    d_status = _e(summ.get("drift_status", "—"))
    p_status = _e(summ.get("prediction_monitoring_status", "—"))
    v_cls = _status_class(summ.get("validation_status", ""))
    d_cls = _status_class(summ.get("drift_status", ""))
    p_cls = _status_class(summ.get("prediction_monitoring_status", ""))

    ov_cls = _status_class(overall)
    ov_text = _e(overall)
    sys_text = _e(decision.get("system_status", "—"))

    lines = [
        '<section class="batch">',
        f'  <h2 id="{slug}">{display}</h2>',
        "  <p><strong>Overall status:</strong> "
        f'<span class="{ov_cls}">{ov_text}</span>',
        f" · <strong>Decision (system):</strong> {sys_text}",
        f" · <strong>Alerts:</strong> {len(alerts)}</p>",
        "  <p class='muted'>"
        f"Batch {_e(rm.get('batch_index'))} of {_e(rm.get('n_batches'))}"
        f" · Generated (UTC): {_e(rm.get('generated_at'))}"
        f" · File: {_e(rm.get('current_batch_file'))}</p>",
        "  <h3>Severity overview</h3>",
        "  <p><strong>Worst alert level:</strong> ",
        highest,
        f" · Counts: CRITICAL={crit}, WARNING={warn}, INFO={info}</p>",
        f"  <p class='muted'>{attention}</p>",
        "  <h3>Decision summary</h3>",
        "  <p><strong>Primary issues</strong></p>",
        f"  <ul>{issues_html}</ul>",
        "  <p><strong>Recommended actions</strong></p>",
        f"  <ul>{actions_html}</ul>",
        "  <h3>Layer status (validation / drift / prediction)</h3>",
        "  <table class='compact'>",
        f"    <tr><th>Validation</th><td><span class='{v_cls}'>{v_status}</span></td></tr>",
        f"    <tr><th>Drift</th><td><span class='{d_cls}'>{d_status}</span></td></tr>",
        f"    <tr><th>Prediction monitoring</th><td><span class='{p_cls}'>{p_status}</span></td></tr>",
        "  </table>",
        "  <h3>Alerts</h3>",
        "  " + _render_alerts_table(alerts),
        "</section>",
    ]
    return "\n".join(lines)


def render_run_html(reports: list[dict]) -> str:
    """Build one HTML document summarizing every batch report in order."""
    if not reports:
        return ""

    first = reports[0]
    rm0 = first.get("run_metadata") or {}
    title = "ML monitoring — run report"

    run_rows_parts = []
    for r in reports:
        ds = r.get("decision_summary") or {}
        oa = r.get("overall_status", "")
        run_rows_parts.append(
            "<tr><td>"
            + _e(r.get("batch_name"))
            + "</td><td><span class='"
            + _status_class(oa)
            + "'>"
            + _e(oa)
            + "</span></td><td>"
            + _e(ds.get("system_status", "—"))
            + "</td><td>"
            + str(r.get("alert_count", 0))
            + "</td></tr>"
        )
    run_rows = "".join(run_rows_parts)

    meta_rows = "".join(
        f"<tr><th>{_e(k)}</th><td>{_e(rm0.get(k))}</td></tr>" for k in _RUN_META_KEYS
    )

    batches_html = "\n".join(_render_batch(r) for r in reports)

    te = _e(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{te}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; line-height: 1.5;
      max-width: 920px; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; color: #1a1a1a; }}
    h1 {{ font-size: 1.5rem; border-bottom: 2px solid #333; padding-bottom: 0.35rem; }}
    h2 {{ font-size: 1.2rem; margin-top: 2rem; border-bottom: 1px solid #bbb; padding-bottom: 0.2rem; }}
    h3 {{ font-size: 1.05rem; margin-top: 1.25rem; }}
    table {{ width: 100%; border-collapse: collapse; margin: 0.5rem 0 1rem; font-size: 0.92rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.45rem 0.65rem; text-align: left; vertical-align: top; }}
    th {{ background: #f4f4f4; font-weight: 600; }}
    table.compact th {{ width: 12rem; }}
    .muted {{ color: #555; font-size: 0.9rem; }}
    .tag-critical {{ font-weight: 600; color: #7f1d1d; }}
    .tag-warning {{ font-weight: 600; color: #92400e; }}
    .tag-ok {{ color: #14532d; }}
    section.batch {{ border-left: 3px solid #ddd; padding-left: 1rem; margin-top: 1.5rem; }}
    footer {{ margin-top: 2.5rem; padding-top: 1rem; border-top: 1px solid #ddd; font-size: 0.85rem; color: #666; }}
  </style>
</head>
<body>
  <h1>{te}</h1>
  <p class="muted">Static export from batch monitoring JSON. Open alongside <code>artifacts/reports/*.json</code> for full detail.</p>

  <h2>Run metadata</h2>
  <table class="compact">{meta_rows}</table>
  <p class="muted">Per-batch timestamps and file paths are listed under each batch below.</p>

  <h2>Run overview</h2>
  <table>
    <thead><tr><th>Batch</th><th>Overall</th><th>System (decision)</th><th>Alert count</th></tr></thead>
    <tbody>{run_rows}</tbody>
  </table>

  <h2>Batch details</h2>
  {batches_html}

  <footer>
    Generated as static HTML by the monitoring pipeline. No external assets.
    Run ID: {_e(rm0.get("run_id"))} · Pipeline: {_e(rm0.get("pipeline_version"))}
  </footer>
</body>
</html>
"""


def export_run_html_report(
    reports: list[dict],
    output_path: str | Path | None = None,
) -> Path | None:
    """
    Write monitoring_run_report.html (or output_path) under artifacts/reports.
    Returns path if written, or None if reports is empty.
    """
    if not reports:
        return None
    path = Path(output_path or ARTIFACTS_REPORTS_DIR / "monitoring_run_report.html")
    ensure_dir(path.parent)
    path.write_text(render_run_html(reports), encoding="utf-8")
    return path
