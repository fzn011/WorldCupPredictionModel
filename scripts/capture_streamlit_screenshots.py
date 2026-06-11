"""Capture full-page screenshots of main Streamlit pages via sidebar navigation."""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8502"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "screenshots"

MAIN_PAGES = [
    "Home",
    "Match Predictor",
    "Tournament Forecast",
    "World Cup Awards",
    "Reports",
    "Data Quality",
]


def _slug(name: str) -> str:
    return name.lower().replace(" ", "-")


def capture() -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(5000)

        sidebar = page.locator('section[data-testid="stSidebar"]')
        for idx, page_name in enumerate(MAIN_PAGES, start=1):
            if page_name != "Home":
                label = sidebar.get_by_text(page_name, exact=True)
                label.first.click(timeout=30_000)
                page.wait_for_timeout(4500)

            out = OUTPUT_DIR / f"{idx:02d}-{_slug(page_name)}.png"
            page.screenshot(path=str(out), full_page=True)
            saved.append(out)
            print(f"Saved {out}")

        browser.close()

    return saved


if __name__ == "__main__":
    paths = capture()
    print(f"Captured {len(paths)} screenshots in {OUTPUT_DIR}")
