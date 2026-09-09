"""app/browser/dom_analyzer.py — Extract semantic elements from the page DOM."""
from __future__ import annotations
from typing import TYPE_CHECKING, List
from app.browser.state import ElementInfo

if TYPE_CHECKING:
    from playwright.sync_api import Page


def extract_buttons(page: "Page") -> List[ElementInfo]:
    """Extracts visible, actionable buttons from the DOM."""
    elements = []
    try:
        handles = page.query_selector_all("button, [role='button'], input[type='submit'], input[type='button'], a.btn")
        for h in handles[:20]:
            try:
                if not h.is_visible():
                    continue
                text = (h.inner_text() or h.get_attribute("aria-label") or h.get_attribute("value") or "").strip()
                if not text:
                    continue
                selector = _safe_selector(h, page)
                elements.append(ElementInfo(tag="button", text=text, selector=selector))
            except Exception:
                continue
    except Exception:
        pass
    return elements


def extract_inputs(page: "Page") -> List[ElementInfo]:
    """Extracts visible form inputs."""
    elements = []
    try:
        handles = page.query_selector_all("input:not([type='hidden']), textarea, select")
        for h in handles[:15]:
            try:
                if not h.is_visible():
                    continue
                input_type = h.get_attribute("type") or h.evaluate("el => el.tagName.toLowerCase()")
                placeholder = h.get_attribute("placeholder") or ""
                name = h.get_attribute("name") or h.get_attribute("id") or h.get_attribute("aria-label") or ""
                selector = _safe_selector(h, page)
                elements.append(
                    ElementInfo(
                        tag="input",
                        text="",
                        input_type=input_type,
                        placeholder=placeholder,
                        name=name,
                        selector=selector,
                    )
                )
            except Exception:
                continue
    except Exception:
        pass
    return elements


def extract_links(page: "Page") -> List[ElementInfo]:
    """Extracts visible links with meaningful text."""
    elements = []
    try:
        handles = page.query_selector_all("a[href]")
        for h in handles[:20]:
            try:
                if not h.is_visible():
                    continue
                text = (h.inner_text() or "").strip()
                href = h.get_attribute("href") or ""
                if not text or len(text) < 2:
                    continue
                elements.append(ElementInfo(tag="a", text=text[:80], href=href[:200]))
            except Exception:
                continue
    except Exception:
        pass
    return elements


def get_visible_text(page: "Page", max_chars: int = 600) -> str:
    """Gets visible body text, truncated to avoid LLM token bloat."""
    try:
        text = page.evaluate("""
            () => {
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    { acceptNode: n => n.textContent.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT }
                );
                const parts = [];
                let node;
                while ((node = walker.nextNode()) && parts.join(' ').length < 1500) {
                    const t = node.textContent.trim();
                    if (t.length > 2) parts.push(t);
                }
                return parts.join(' ');
            }
        """)
        return (text or "")[:max_chars]
    except Exception:
        return ""


def classify_page_type(url: str, title: str, visible_text: str) -> str:
    """Classifies the page type using heuristics."""
    url_l = url.lower()
    title_l = title.lower()
    text_l = visible_text.lower()

    if any(k in url_l for k in ["checkout", "payment", "pay", "billing"]):
        return "checkout"
    if any(k in url_l for k in ["cart", "basket", "bag"]):
        return "cart"
    if any(k in url_l for k in ["login", "signin", "sign-in", "auth"]):
        return "login"
    if any(k in url_l for k in ["search", "q=", "query"]):
        return "search_results"
    if any(k in url_l for k in ["product", "item", "dp/", "p/"]):
        return "product"
    if "captcha" in text_l or "verify you are human" in text_l:
        return "captcha"
    return "general"


def _safe_selector(handle, page: "Page") -> str:
    """Generates a best-effort selector for the element."""
    try:
        _id = handle.get_attribute("id")
        if _id:
            return f"#{_id}"
        aria = handle.get_attribute("aria-label")
        if aria:
            return f"[aria-label='{aria}']"
        name = handle.get_attribute("name")
        if name:
            return f"[name='{name}']"
    except Exception:
        pass
    return ""
