"""app/browser/result_extractor.py — Extract structured results from pages."""
from __future__ import annotations
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page


def extract_search_results(page: "Page", max_results: int = 8) -> List[Dict[str, Any]]:
    """
    Extracts product/result cards from search results pages.
    Works generically across most e-commerce and search sites.
    """
    results = []
    try:
        # Generic result card selector — works on most sites
        cards = page.query_selector_all(
            "article, [data-component-type='s-search-result'], "
            ".s-result-item, .product-item, ._1AtVbE, [class*='product'], "
            "[class*='result'], [class*='card']"
        )

        for card in cards[:max_results]:
            try:
                if not card.is_visible():
                    continue
                title_el = card.query_selector("h2, h3, [class*='title'], [class*='name']")
                price_el = card.query_selector(
                    "[class*='price'], [class*='Price'], .a-price-whole, ._30jeq3"
                )
                rating_el = card.query_selector(
                    "[aria-label*='stars'], [aria-label*='rating'], ._3LWZlK, .a-icon-alt"
                )
                link_el = card.query_selector("a[href]")

                title = title_el.inner_text().strip() if title_el else ""
                price = price_el.inner_text().strip() if price_el else ""
                rating = rating_el.get_attribute("aria-label") or (rating_el.inner_text().strip() if rating_el else "")
                href = link_el.get_attribute("href") if link_el else ""

                if title:
                    results.append({
                        "title": title[:80],
                        "price": price[:20],
                        "rating": rating[:20],
                        "url": href[:200],
                        "index": len(results) + 1,
                    })
            except Exception:
                continue
    except Exception:
        pass

    return results


def summarize_results_for_voice(results: List[Dict[str, Any]]) -> str:
    """Creates a short voice-friendly summary of search results."""
    if not results:
        return "I couldn't find any results on this page."

    parts = [f"I found {len(results)} results."]
    for i, r in enumerate(results[:3], 1):
        price_str = f" for {r['price']}" if r.get("price") else ""
        parts.append(f"Option {i}: {r['title']}{price_str}.")

    if len(results) > 3:
        parts.append(f"And {len(results) - 3} more.")

    return " ".join(parts)
