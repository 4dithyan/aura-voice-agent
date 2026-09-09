"""app/browser/state.py — Compact browser page state representation."""
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class ElementInfo:
    tag: str
    text: str
    role: str = ""
    name: str = ""
    selector: str = ""
    href: str = ""
    input_type: str = ""
    placeholder: str = ""


@dataclass
class BrowserState:
    url: str = ""
    title: str = ""
    page_type: str = "unknown"
    visible_text: str = ""
    buttons: List[ElementInfo] = field(default_factory=list)
    links: List[ElementInfo] = field(default_factory=list)
    inputs: List[ElementInfo] = field(default_factory=list)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    screenshot_path: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: str = ""

    def to_compact_dict(self, max_items: int = 8) -> Dict[str, Any]:
        """Returns a compact summary safe to send to the LLM."""
        return {
            "url": self.url,
            "title": self.title,
            "page_type": self.page_type,
            "visible_text": self.visible_text[:500] if self.visible_text else "",
            "buttons": [
                {"text": b.text, "name": b.name, "selector": b.selector}
                for b in self.buttons[:max_items]
            ],
            "inputs": [
                {
                    "type": i.input_type,
                    "placeholder": i.placeholder,
                    "name": i.name,
                    "selector": i.selector,
                }
                for i in self.inputs[:max_items]
            ],
            "links": [
                {"text": l.text, "href": l.href}
                for l in self.links[:max_items]
            ],
        }
