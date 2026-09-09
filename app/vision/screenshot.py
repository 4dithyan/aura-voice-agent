"""app/vision/screenshot.py — Screenshot capture with automatic cache cleanup."""
import time
from pathlib import Path
from datetime import datetime
from app.config import settings


def capture_screenshot(page) -> str:
    """Takes a screenshot of the current Playwright page and saves it."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = settings.SCREENSHOTS_DIR / f"{ts}.png"

    try:
        page.screenshot(path=str(path), full_page=False)
        _cleanup_old_screenshots()
        return str(path)
    except Exception as e:
        print(f"[Screenshot] Failed: {e}")
        return ""


def _cleanup_old_screenshots():
    """Removes old screenshots beyond the configured cache limit."""
    try:
        files = sorted(
            settings.SCREENSHOTS_DIR.glob("*.png"),
            key=lambda f: f.stat().st_mtime,
        )
        while len(files) > settings.MAX_SCREENSHOT_CACHE:
            files[0].unlink(missing_ok=True)
            files = files[1:]
    except Exception:
        pass
