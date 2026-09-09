"""app/browser/controller.py — Playwright BrowserController abstraction."""
from __future__ import annotations
import time
from typing import Optional, List, Dict, Any
from pathlib import Path

from app.browser.state import BrowserState, ElementInfo
from app.browser.dom_analyzer import (
    extract_buttons, extract_inputs, extract_links,
    get_visible_text, classify_page_type,
)
from app.vision.screenshot import capture_screenshot
from app.core.events import emitter
from app.config import settings


class BrowserController:
    """
    Playwright abstraction. DOM-first strategy — vision is only invoked externally
    when the controller cannot resolve an element.
    """

    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._is_open = False

    # ------------------------------------------------------------------ lifecycle

    def open(self) -> bool:
        """Launches Playwright Chromium."""
        try:
            from playwright.sync_api import sync_playwright
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=settings.BROWSER_HEADLESS,
                args=["--no-first-run", "--disable-extensions"],
            )
            self._context = self._browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
            )
            self._page = self._context.new_page()
            self._is_open = True
            emitter.emit("browser_opened")
            return True
        except Exception as e:
            print(f"[Browser] Failed to open: {e}")
            return False

    def close(self):
        """Closes Playwright browser."""
        try:
            if self._page:
                self._page.close()
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        finally:
            self._is_open = False
            self._page = None

    @property
    def is_open(self) -> bool:
        return self._is_open and self._page is not None

    # ------------------------------------------------------------------ navigation

    def navigate(self, url: str, timeout: int = 15000) -> bool:
        """Navigates to a URL."""
        if not url.startswith("http"):
            url = "https://" + url
        try:
            emitter.emit("navigation_started", url=url)
            self._page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            self._handle_common_overlays()
            emitter.emit("navigation_completed", url=self._page.url)
            return True
        except Exception as e:
            print(f"[Browser] Navigate failed: {e}")
            return False

    def go_back(self) -> bool:
        try:
            self._page.go_back(wait_until="domcontentloaded", timeout=8000)
            return True
        except Exception:
            return False

    def go_forward(self) -> bool:
        try:
            self._page.go_forward(wait_until="domcontentloaded", timeout=8000)
            return True
        except Exception:
            return False

    def reload(self) -> bool:
        try:
            self._page.reload(wait_until="domcontentloaded", timeout=8000)
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------ interaction

    def click(self, target: str) -> bool:
        """
        Clicks an element by text, aria-label, selector, or role.
        DOM-first — tries multiple strategies before failing.
        """
        emitter.emit("action_started", action="click", target=target)
        strategies = [
            lambda: self._page.get_by_text(target, exact=False).first.click(timeout=4000),
            lambda: self._page.get_by_role("button", name=target).first.click(timeout=4000),
            lambda: self._page.get_by_role("link", name=target).first.click(timeout=4000),
            lambda: self._page.locator(f"[aria-label*='{target}']").first.click(timeout=4000),
            lambda: self._page.locator(target).first.click(timeout=4000),
        ]
        for strategy in strategies:
            try:
                strategy()
                self._wait_for_settle()
                emitter.emit("action_completed", action="click", target=target, success=True)
                return True
            except Exception:
                continue
        emitter.emit("action_completed", action="click", target=target, success=False)
        return False

    def fill(self, field: str, value: str) -> bool:
        """Fills an input field identified by placeholder, name, label, or selector."""
        emitter.emit("action_started", action="fill", target=field, value=value[:20])
        strategies = [
            lambda: self._page.get_by_placeholder(field).first.fill(value, timeout=4000),
            lambda: self._page.get_by_label(field).first.fill(value, timeout=4000),
            lambda: self._page.locator(f"[name='{field}']").first.fill(value, timeout=4000),
            lambda: self._page.locator(f"[id='{field}']").first.fill(value, timeout=4000),
            lambda: self._page.locator(field).first.fill(value, timeout=4000),
        ]
        for strategy in strategies:
            try:
                strategy()
                emitter.emit("action_completed", action="fill", target=field, success=True)
                return True
            except Exception:
                continue
        emitter.emit("action_completed", action="fill", target=field, success=False)
        return False

    def press_key(self, key: str) -> bool:
        try:
            self._page.keyboard.press(key)
            return True
        except Exception:
            return False

    def scroll(self, direction: str = "down", amount: int = 400) -> bool:
        try:
            delta = amount if direction == "down" else -amount
            self._page.evaluate(f"window.scrollBy(0, {delta})")
            return True
        except Exception:
            return False

    def click_nth_result(self, n: int) -> bool:
        """Clicks the nth visible result/card link on a search results page."""
        try:
            cards = self._page.query_selector_all(
                "article a, .s-result-item h2 a, ._1AtVbE a, "
                "[class*='product'] a, [class*='result'] a, [class*='card'] a"
            )
            visible = [c for c in cards if c.is_visible()]
            if n <= len(visible):
                visible[n - 1].click()
                self._wait_for_settle()
                return True
        except Exception:
            pass
        return False

    # ------------------------------------------------------------------ state

    def get_page_state(self) -> BrowserState:
        """Returns a compact BrowserState from the current page DOM."""
        try:
            url = self._page.url
            title = self._page.title()
            visible_text = get_visible_text(self._page)
            buttons = extract_buttons(self._page)
            inputs = extract_inputs(self._page)
            links = extract_links(self._page)
            page_type = classify_page_type(url, title, visible_text)

            state = BrowserState(
                url=url,
                title=title,
                page_type=page_type,
                visible_text=visible_text,
                buttons=buttons,
                inputs=inputs,
                links=links,
            )
            emitter.emit("page_analyzed", page_type=page_type, url=url)
            return state
        except Exception as e:
            return BrowserState(error=str(e))

    def screenshot(self) -> str:
        """Takes a screenshot and returns the path."""
        if not self._page:
            return ""
        path = capture_screenshot(self._page)
        if path:
            emitter.emit("screenshot_taken", path=path)
        return path

    def get_url(self) -> str:
        try:
            return self._page.url
        except Exception:
            return ""

    def get_title(self) -> str:
        try:
            return self._page.title()
        except Exception:
            return ""

    # ------------------------------------------------------------------ private helpers

    def _wait_for_settle(self, timeout: int = 3000):
        """Waits briefly for the page to settle after an action."""
        try:
            self._page.wait_for_load_state("domcontentloaded", timeout=timeout)
        except Exception:
            time.sleep(0.5)

    def _handle_common_overlays(self):
        """Dismisses common cookie banners and popups."""
        dismiss_texts = [
            "Accept", "Accept All", "Accept Cookies", "Got it", "OK", "Close",
            "Agree", "I Accept", "Allow all", "Decline"
        ]
        for text in dismiss_texts[:3]:
            try:
                btn = self._page.get_by_text(text, exact=True).first
                if btn.is_visible():
                    btn.click(timeout=2000)
                    time.sleep(0.3)
                    break
            except Exception:
                continue


# Singleton instance shared across the session
_controller: Optional[BrowserController] = None


def get_controller() -> BrowserController:
    global _controller
    if _controller is None:
        _controller = BrowserController()
    return _controller


def reset_controller():
    global _controller
    if _controller and _controller.is_open:
        _controller.close()
    _controller = None
