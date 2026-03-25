"""Create directories if needed. IMPLEMENTATION_REFERENCE."""
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    """Ensure directory exists; create if not. Returns path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
