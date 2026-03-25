"""
Streamlit monitoring viewer: batch selector, status metrics, alerts, drift table, score histogram.
Paths resolve from the repository root (not the process cwd). If you start Streamlit with an absolute
path to this file, ``src`` is added to ``sys.path`` so imports still work.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
import streamlit as st

from src.reporting.decision_summary import build_decision_summary
from src.reporting.severity import (
    CRITICAL,
    INFO,
    OK,
    WARNING,
    build_severity_overview,
    normalize_severity,
    severity_rank,
)
from src.utils.paths import ARTIFACTS_DRIFT_DIR, ARTIFACTS_REPORTS_DIR, DATA_CURRENT_DIR

OVERVIEW_CSV = ARTIFACTS_REPORTS_DIR / "monitoring_overview.csv"

_OVERVIEW_RENAME = {
    "batch_name": "Batch file",
    "overall_status": "Overall",
    "validation_status": "Validation",
    "drift_status": "Drift",
    "prediction_monitoring_status": "Prediction monitoring",
    "alert_count": "Number of alerts",
}

_DRIFT_DISPLAY_RENAME = {
    "psi": "PSI",
    "ks_statistic": "KS statistic",
    "ks_pvalue": "KS p-value",
    "severity": "Drift severity",
    "unseen_count": "Unseen categories",
}

# Worst-first ordering for the headline status (CRITICAL most severe)
_TOP_STATUS_RANK = {CRITICAL: 0, WARNING: 1, INFO: 2, OK: 3}


def _layer_status_label(value) -> str:
    m = {"ok": "OK", "warning": "WARNING", "critical": "CRITICAL"}
    if value is None:
        return "—"
    return m.get(str(value).lower(), str(value).upper())


def _overall_to_status_label(overall: str) -> str:
    m = {"ok": OK, "warning": WARNING, "critical": CRITICAL}
    o = str(overall).lower()
    if o in m:
        return m[o]
    if o == "unknown":
        return WARNING
    return WARNING


def _worst_headline_status(overall: str, decision_system: str, highest_alert: str) -> str:
    """Worst of pipeline overall, decision roll-up, and peak alert severity."""
    candidates = [
        _overall_to_status_label(overall),
        str(decision_system or OK).strip().upper(),
        str(highest_alert or OK).strip().upper(),
    ]
    normalized = []
    for c in candidates:
        if c == OK:
            normalized.append(OK)
        elif c in (CRITICAL, WARNING, INFO):
            normalized.append(c)
        else:
            normalized.append(WARNING)
    worst_rank = min(_TOP_STATUS_RANK[s] for s in normalized)
    for label, r in _TOP_STATUS_RANK.items():
        if r == worst_rank:
            return label
    return WARNING


def _alerts_table_rows(alerts: list) -> list[dict]:
    rows = []
    for a in alerts:
        row = dict(a)
        row["severity"] = normalize_severity(a.get("severity"))
        rows.append(row)
    rows.sort(key=lambda r: severity_rank(r.get("severity")))
    return rows


def _churn_score_histogram(scores: pd.Series) -> pd.DataFrame:
    """Equal-width bins on [0, 1] for model scores (not raw value_counts)."""
    arr = scores.dropna().to_numpy(dtype=float)
    if arr.size == 0:
        return pd.DataFrame()
    counts, edges = np.histogram(arr, bins=30, range=(0.0, 1.0))
    mids = (edges[:-1] + edges[1:]) / 2
    return pd.DataFrame({"bin_center": mids, "count": counts}).set_index("bin_center")


def _render_run_overview_table(overview: pd.DataFrame) -> None:
    st.subheader("All batches (this run)")
    st.caption("From `monitoring_overview.csv`: one row per file under `data/current/` in the same execution.")
    display = overview.rename(columns={k: v for k, v in _OVERVIEW_RENAME.items() if k in overview.columns})
    st.dataframe(display, use_container_width=True, hide_index=True)


def _render_system_status(headline: str, sov: dict, n_alerts: int) -> None:
    st.subheader("System status")
    counts = sov.get("counts") or {}
    c0, c1, c2, c3 = st.columns(4)
    c0.metric("Overall", headline)
    c1.metric("CRITICAL", int(counts.get(CRITICAL, 0)))
    c2.metric("WARNING", int(counts.get(WARNING, 0)))
    c3.metric("INFO", int(counts.get(INFO, 0)))
    st.caption(sov.get("attention_priority", ""))
    if headline == CRITICAL:
        st.error("Action required: resolve CRITICAL items before treating this batch as safe.")
    elif headline == WARNING:
        st.warning("Investigate WARNING-level issues and confirm impact before promotion.")
    elif headline == INFO and n_alerts > 0:
        st.info("Only INFO-level alerts; use as context unless your runbook says otherwise.")
    else:
        st.success("No CRITICAL or WARNING conditions for this batch.")


def main():
    st.set_page_config(page_title="ML Monitoring — viewer", layout="wide")

    st.title("ML Monitoring & Data Quality Pipeline")
    st.markdown(
        "Live read-only view of batch reports and scores from the last monitoring run."
    )
    st.caption("Portfolio demo — not a production monitoring system.")

    if not OVERVIEW_CSV.exists():
        st.warning(
            "No overview CSV found. From the repository root, run: "
            "`python -m src.simulation.run_all_simulation` then "
            "`python -m src.pipeline.run_full_monitoring`"
        )
        return

    overview = pd.read_csv(OVERVIEW_CSV)
    batch_names = overview["batch_name"].tolist()
    st.caption(
        "Choose a batch — sections below are for that selection. Run-wide comparison table is at the bottom."
    )
    selected = st.selectbox(
        "Batch to inspect",
        batch_names,
        index=0 if batch_names else None,
        help="Files analysed in the last `run_full_monitoring` execution.",
    )

    if not selected:
        return

    stem = Path(selected).stem
    report_path = ARTIFACTS_REPORTS_DIR / f"report_{stem}.json"
    if not report_path.exists():
        st.error(f"Report missing: `{report_path}`")
        _render_run_overview_table(overview)
        return

    with open(report_path, encoding="utf-8") as f:
        report = json.load(f)

    overall = report.get("overall_status", "unknown")
    summary = report.get("summary", {})
    alerts = report.get("alerts") or []
    decision = report.get("decision_summary") or build_decision_summary(
        report.get("overall_status") or "ok",
        alerts,
    )
    sov = decision.get("severity_overview") or build_severity_overview(alerts)
    headline = _worst_headline_status(
        str(overall),
        decision.get("system_status", OK),
        sov.get("highest_alert_severity", OK),
    )

    st.divider()
    _render_system_status(headline, sov, len(alerts))

    st.subheader("Decision summary")
    st.markdown("**Primary issues**")
    if decision.get("primary_issues"):
        for line in decision["primary_issues"]:
            st.markdown(f"- {line}")
    else:
        st.markdown("- None")
    st.markdown("**Recommended actions**")
    for line in decision.get("recommended_actions", []):
        st.markdown(f"- {line}")

    rm = report.get("run_metadata") or {}
    st.subheader("Run metadata")
    if rm:
        st.caption("Shared across all batches in this run unless noted.")
        r1, r2, r3 = st.columns(3)
        r1.metric("Pipeline version", str(rm.get("pipeline_version", "—")))
        sv = rm.get("schema_version")
        r2.metric("Schema version", str(sv) if sv is not None else "—")
        r3.metric("Batches in run", str(rm.get("n_batches", "—")))
        st.markdown(f"**run_id:** `{rm.get('run_id', '—')}`")
        st.markdown(f"**generated_at (UTC):** `{rm.get('generated_at', '—')}`")
        st.caption(
            f"Reference: `{rm.get('reference_dataset', '—')}` · "
            f"Current: `{rm.get('current_batch_file', '—')}`"
        )
    else:
        st.caption("No `run_metadata` in this file. Re-run `python -m src.pipeline.run_full_monitoring` to populate it.")

    st.subheader("Monitoring layers")
    st.caption("Roll-up status for this batch (validation, drift vs reference, prediction monitoring).")
    c1, c2, c3 = st.columns(3)
    c1.metric("Validation", _layer_status_label(summary.get("validation_status")))
    c2.metric("Drift", _layer_status_label(summary.get("drift_status")))
    c3.metric("Prediction monitoring", _layer_status_label(summary.get("prediction_monitoring_status")))

    st.subheader("Alerts")
    st.caption("Sorted by severity (CRITICAL first). Same rules as in the JSON report.")
    if alerts:
        display_rows = _alerts_table_rows(alerts)
        alert_rows = pd.DataFrame(display_rows)
        cols = ["severity", "type", "message"]
        alert_rows = alert_rows[[c for c in cols if c in alert_rows.columns]]
        alert_display = alert_rows.rename(
            columns={"severity": "Severity", "type": "Type", "message": "Message"}
        )
        st.dataframe(alert_display, use_container_width=True, hide_index=True)
    else:
        st.success("No alerts for this batch.")

    st.subheader("Supporting view")
    st.markdown("**Churn score distribution** (`churn_score`, 30 equal-width bins on [0, 1])")
    current_path = DATA_CURRENT_DIR / selected
    if current_path.exists():
        df = pd.read_csv(current_path)
        if "churn_score" in df.columns:
            hist_df = _churn_score_histogram(df["churn_score"])
            if hist_df.empty:
                st.caption("No non-null churn_score values.")
            else:
                st.bar_chart(hist_df)
        else:
            st.caption("No `churn_score` column in this batch.")
    else:
        st.caption(f"Batch CSV not found at `{current_path}`.")

    st.subheader("Optional details")
    with st.expander("Per-feature drift (table)", expanded=False):
        drift_path = ARTIFACTS_DRIFT_DIR / f"drift_{stem}.json"
        st.caption(
            "Per-column PSI / KS vs reference. Drift severity here is a feature-level label, not the same as alert severity."
        )
        if drift_path.exists():
            with open(drift_path, encoding="utf-8") as f:
                drift = json.load(f)
            per_col = drift.get("per_column", {})
            if per_col:
                rows = [{"column": col, **metrics} for col, metrics in per_col.items()]
                drift_df = pd.DataFrame(rows)
                rename_map = {k: v for k, v in _DRIFT_DISPLAY_RENAME.items() if k in drift_df.columns}
                drift_df = drift_df.rename(columns=rename_map)
                st.dataframe(drift_df, use_container_width=True, hide_index=True)
            else:
                st.caption("No per-column drift metrics.")
        else:
            st.caption(f"No drift file at `{drift_path}`.")

    with st.expander("Full report (JSON)", expanded=False):
        st.json(report)

    _render_run_overview_table(overview)


if __name__ == "__main__":
    main()
