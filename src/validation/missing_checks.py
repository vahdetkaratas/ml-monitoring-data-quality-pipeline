"""Missing rate checks. MONITORING_SYSTEM_DESIGN §3, IMPLEMENTATION_REFERENCE §4."""
import pandas as pd

DEFAULT_MISSING_THRESHOLD = 0.10  # 10%


def check_missing_rates(
    df: pd.DataFrame,
    schema: dict,
    threshold: float = DEFAULT_MISSING_THRESHOLD,
) -> dict:
    """Per-column missing rate; flag columns above threshold. Returns {ok, columns_above_threshold, rates, message}."""
    columns_above = []
    rates = {}
    for col in df.columns:
        if col not in schema:
            continue
        rate = df[col].isna().mean()
        rates[col] = round(rate, 4)
        if rate > threshold:
            columns_above.append(col)
    return {
        "ok": len(columns_above) == 0,
        "columns_above_threshold": columns_above,
        "rates": rates,
        "message": "Missing rates OK" if not columns_above else f"Above {threshold}: {columns_above}",
    }
