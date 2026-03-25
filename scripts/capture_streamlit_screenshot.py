"""
Optional: refresh reports/figures/streamlit_demo.png from a deployed Streamlit URL.

Requires: pip install playwright && playwright install chromium

Usage (from repo root):
    python scripts/capture_streamlit_screenshot.py

Override URL:
    set STREAMLIT_DEMO_URL=https://your-host/ && python scripts/capture_streamlit_screenshot.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_OUT = _ROOT / "reports" / "figures" / "streamlit_demo.png"
_DEFAULT_URL = "https://monitoring.vahdetkaratas.com/"


def main() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        print("Install Playwright first: pip install playwright && playwright install chromium", file=sys.stderr)
        raise SystemExit(1) from e

    url = os.environ.get("STREAMLIT_DEMO_URL", _DEFAULT_URL).strip()
    _OUT.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(url, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(5000)
        page.screenshot(path=str(_OUT), full_page=False)
        browser.close()

    print(f"Wrote {_OUT} ({url})")


if __name__ == "__main__":
    main()
