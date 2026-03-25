"""Prediction monitoring: score distribution, positive rate, threshold. MONITORING_SYSTEM_DESIGN §5, IMPLEMENTATION_REFERENCE §6."""
import pandas as pd
from src.drift.psi import psi_numeric

SCORE_PSI_CRITICAL = 0.3
SCORE_PSI_WARNING = 0.2
POS_RATE_DELTA_CRITICAL = 0.15
POS_RATE_DELTA_WARNING = 0.08


def prediction_monitoring_summary(
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
) -> dict:
    """Score: mean, std, median, p25, p75, PSI. Label: positive_rate, delta. Threshold: rate above 0.5, 0.7. Status critical/warning/ok."""
    if "churn_score" not in reference_df.columns or "churn_score" not in current_df.columns:
        return {"status": "ok", "message": "No churn_score column", "metrics": {}}
    ref_scores = reference_df["churn_score"].dropna()
    cur_scores = current_df["churn_score"].dropna()
    ref_pos = (reference_df["predicted_label"] == 1).mean() if "predicted_label" in reference_df.columns else 0
    cur_pos = (current_df["predicted_label"] == 1).mean() if "predicted_label" in current_df.columns else 0
    pos_rate_delta = abs(cur_pos - ref_pos)
    score_psi = psi_numeric(ref_scores, cur_scores)
    status = "ok"
    if score_psi > SCORE_PSI_CRITICAL or pos_rate_delta > POS_RATE_DELTA_CRITICAL:
        status = "critical"
    elif score_psi > SCORE_PSI_WARNING or pos_rate_delta > POS_RATE_DELTA_WARNING:
        status = "warning"
    q = cur_scores.quantile([0.25, 0.5, 0.75])
    rate_above_05 = (cur_scores >= 0.5).mean()
    rate_above_07 = (cur_scores >= 0.7).mean()
    metrics = {
        "score_mean_current": round(cur_scores.mean(), 4),
        "score_std_current": round(cur_scores.std(), 4),
        "score_median_current": round(q.get(0.5, 0), 4),
        "score_p25_current": round(q.get(0.25, 0), 4),
        "score_p75_current": round(q.get(0.75, 0), 4),
        "positive_rate_reference": round(ref_pos, 4),
        "positive_rate_current": round(cur_pos, 4),
        "positive_rate_delta": round(pos_rate_delta, 4),
        "score_psi": round(score_psi, 4),
        "rate_above_05": round(rate_above_05, 4),
        "rate_above_07": round(rate_above_07, 4),
    }
    return {"status": status, "metrics": metrics}
