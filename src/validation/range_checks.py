"""Range checks for numeric columns (min/max from schema). MONITORING_SYSTEM_DESIGN §3."""
import pandas as pd


def check_ranges(df: pd.DataFrame, schema: dict) -> dict:
    """Check numeric columns are within schema min/max. Returns {ok, out_of_range_columns, message}."""
    out_of_range = []
    for col, spec in schema.items():
        if col not in df.columns or spec.get("dtype") not in ("int", "float"):
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        below_min = "min" in spec and (s < spec["min"]).any()
        above_max = "max" in spec and (s > spec["max"]).any()
        if below_min or above_max:
            out_of_range.append(col)
    return {
        "ok": len(out_of_range) == 0,
        "out_of_range_columns": out_of_range,
        "message": "Ranges OK" if not out_of_range else f"Out of range: {out_of_range}",
    }
