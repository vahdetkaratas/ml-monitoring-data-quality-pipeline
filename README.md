# ML Monitoring & Data Quality Pipeline

[![CI](https://github.com/vahdetkaratas/ml-monitoring-data-quality-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/vahdetkaratas/ml-monitoring-data-quality-pipeline/actions/workflows/ci.yml)

Batch monitoring demo for **tabular** scoring data: validate incoming batches against a JSON schema, compare to a **reference** dataset (numeric/categorical drift, prediction behaviour), and write **JSON reports**, a **CSV overview**, and a **static HTML run report**. Includes a small **Streamlit** app that reads those artifacts.

## Live demo

**Interactive viewer (Streamlit):** [monitoring.vahdetkaratas.com](https://monitoring.vahdetkaratas.com/)

The hosted app is the **interactive** dashboard (pick a batch, see status, alerts, and charts). The **static HTML run summary** is a separate artifact: `artifacts/reports/monitoring_run_report.html` in this repo (open locally or browse on GitHub)—it is produced by `run_full_monitoring`, not by Streamlit.

![Streamlit monitoring viewer](reports/figures/streamlit_demo.png)

To refresh the screenshot after UI changes: `pip install playwright`, `playwright install chromium`, then `python scripts/capture_streamlit_screenshot.py` (optional env `STREAMLIT_DEMO_URL`).

## What this is

- A **local / VPS-friendly** pipeline: CSV in → reports out.
- A **portfolio-sized** example: synthetic reference + five scripted “current” scenarios (clean, missing values, numeric drift, categorical shift, prediction shift).
- **Tests** (`pytest`) for validation, drift, and monitoring helpers.

## What this is not

- Not a live inference API, feature store, or orchestration platform.
- Not a hosted serverless “monitoring SaaS” (no long-running batch jobs on Vercel’s model).
- Drift columns are **defined in code** (`drift_summary.py`), not fully generated from the schema file.

## Requirements

- **Python 3.10+**
- Dependencies: `pip install -r requirements.txt`

Paths to `data/` and `artifacts/` are resolved from the **repository root** (via `src/utils/paths.py`), not from the shell’s current working directory, so the pipeline and Streamlit agree on locations once `src` is importable.

Run CLI commands from the **repository root** so `python -m src.…` resolves the package.

## Sample data and artifacts (git)

**`data/**/*.csv`** and **`artifacts/**`** are **committed on purpose** as small, reproducible demo outputs so you can open `monitoring_run_report.html` or run Streamlit without regenerating everything. To prove a clean run from source only, delete `data/reference/`, `data/current/*.csv`, and `artifacts/`, then run simulation and `run_full_monitoring` as below.

## How to run — simulation

Generates `data/reference/reference_dataset.csv` and five `data/current/current_batch_*.csv` files:

```bash
python -m src.simulation.run_all_simulation
```

## How to run — monitoring pipeline

Reads reference + every `data/current/current_batch_*.csv`, writes:

- `artifacts/reports/report_<batch>.json` — validation, drift, prediction summary, alerts  
- `artifacts/reports/monitoring_overview.csv` — one row per batch  
- `artifacts/reports/monitoring_run_report.html` — static, shareable summary of the full run  
- `artifacts/drift/drift_<batch>.json` — per-feature drift metrics  

```bash
python -m src.pipeline.run_full_monitoring
```

## How to run — Streamlit report viewer

After the pipeline has run at least once:

```bash
streamlit run src/demo/streamlit_app.py
```

Open the URL Streamlit prints (default `http://localhost:8501`). The app loads `monitoring_overview.csv` and the per-batch JSON/CSV from `artifacts/` and `data/current/`.

## Outputs (quick reference)

| Path | Content |
|------|--------|
| `data/metadata/schema_definition.json` | Column contract (types, ranges, categoricals) |
| `data/reference/reference_dataset.csv` | Baseline for drift / prediction monitoring |
| `data/current/current_batch_*.csv` | Incoming batches |
| `artifacts/reports/report_*.json` | Full report + alerts |
| `artifacts/reports/monitoring_overview.csv` | Batch-level status table |
| `artifacts/reports/monitoring_run_report.html` | Static HTML run summary (all batches) |
| `artifacts/drift/drift_*.json` | PSI / KS / categorical metrics |

## Tests

```bash
python -m pytest tests -q
```

On every push / PR to `main`, **GitHub Actions** runs the same test suite (see `.github/workflows/ci.yml`).

## Why VPS (not Vercel) for a “live” demo

- **Streamlit** and the **batch pipeline** expect a normal Python process and filesystem writes under `artifacts/`. That matches a **VPS**, container, or PaaS with a persistent disk (or ephemeral disk for a demo).
- **Vercel** is ideal for **static** sites or short-lived functions; it is a poor fit for running this pipeline continuously or hosting Streamlit without extra complexity. For a public link without running Python, publish the **GitHub repo** and optionally a **static** summary page; for an interactive viewer, use **VPS + Streamlit** (or Docker on any host).

## More documentation

Index: **`docs/README.md`**. Design: **`docs/MONITORING_SYSTEM_DESIGN.md`**. Milestones: **`docs/MILESTONES.md`**. Scope and trade-offs: **`docs/PROJECT_DECISION_RECORD.md`**. Layout and constants: **`docs/IMPLEMENTATION_REFERENCE.md`**.
