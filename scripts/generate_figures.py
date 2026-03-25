"""
Generate reports/figures: architecture, drift chart, prediction chart. MILESTONES M6, IMPLEMENTATION_REFERENCE §12.
Run from repo root: python scripts/generate_figures.py
"""
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from src.utils.paths import REPO_ROOT

FIGURES_DIR = REPO_ROOT / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def save_architecture():
    """Pipeline overview: Validation -> Drift -> Prediction -> Report."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    boxes = [
        (1, 2, "Data\nValidation"),
        (3.5, 2, "Drift\nDetection"),
        (6, 2, "Prediction\nMonitor"),
        (8, 2, "Report\n& Alerts"),
    ]
    for i, (x, y, label) in enumerate(boxes):
        rect = mpatches.FancyBboxPatch((x, y - 0.4), 1.6, 0.8, boxstyle="round,pad=0.05", facecolor="lightblue", edgecolor="black")
        ax.add_patch(rect)
        ax.text(x + 0.8, y, label, ha="center", va="center", fontsize=9)
        if i < len(boxes) - 1:
            ax.annotate("", xy=(x + 1.8, y), xytext=(x + 1.6, y), arrowprops=dict(arrowstyle="->"))
    ax.set_title("ML Monitoring Pipeline")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "architecture.png", dpi=100, bbox_inches="tight")
    plt.close()
    print(f"Saved {FIGURES_DIR / 'architecture.png'}")


def save_drift_chart():
    """Placeholder drift chart (PSI by feature)."""
    fig, ax = plt.subplots(figsize=(6, 4))
    features = ["tenure", "monthly_charges", "contract", "churn_score"]
    psi_vals = [0.05, 0.22, 0.35, 0.12]
    colors = ["green" if p < 0.2 else "orange" if p < 0.3 else "red" for p in psi_vals]
    ax.bar(features, psi_vals, color=colors)
    ax.axhline(0.2, color="gray", linestyle="--", label="Warning (0.2)")
    ax.axhline(0.3, color="gray", linestyle=":", label="Critical (0.3)")
    ax.set_ylabel("PSI")
    ax.set_title("Drift by feature (example)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "drift_chart.png", dpi=100, bbox_inches="tight")
    plt.close()
    print(f"Saved {FIGURES_DIR / 'drift_chart.png'}")


def save_prediction_chart():
    """Placeholder prediction score distribution."""
    fig, ax = plt.subplots(figsize=(6, 4))
    import numpy as np
    scores = np.clip(np.random.beta(2, 5, 500), 0, 1)
    ax.hist(scores, bins=20, color="steelblue", edgecolor="white")
    ax.axvline(0.5, color="red", linestyle="--", label="Threshold 0.5")
    ax.set_xlabel("Churn score")
    ax.set_ylabel("Count")
    ax.set_title("Prediction score distribution (example)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "prediction_chart.png", dpi=100, bbox_inches="tight")
    plt.close()
    print(f"Saved {FIGURES_DIR / 'prediction_chart.png'}")


if __name__ == "__main__":
    save_architecture()
    save_drift_chart()
    save_prediction_chart()
    print("Done.")
