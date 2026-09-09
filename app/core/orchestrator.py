"""app/core/orchestrator.py — Central dispatcher: PC Agent vs Browser Agent."""
import json
from typing import Tuple
from app.agent.ollama_client import generate_text
from app.config import settings

# Keywords that unambiguously route to the browser agent (fast path, no LLM needed)
BROWSER_KEYWORDS = [
    "search", "google", "open website", "open flipkart", "open amazon",
    "open youtube", "open chrome", "navigate to", "go to", "browse",
    "find on", "look up", "search for", "open the browser", "open browser",
    "website", "web", "url", "http", "www.", ".com", ".in", ".org",
    "hotel", "flight", "book", "shop", "buy", "order", "checkout",
    "add to cart", "product", "price", "results", "compare",
]

STOP_COMMANDS = ["stop", "cancel", "cancel task", "jarvis stop", "stop task"]
PAUSE_COMMANDS = ["pause", "wait", "hold on"]
RESUME_COMMANDS = ["resume", "continue", "go on", "proceed"]


class TaskOrchestrator:
    """
    Decides whether a command routes to the existing PC Agent or the Browser Agent.
    Keeps a reference to the active browser agent for pause/cancel/resume support.
    """

    def __init__(self):
        self._active_browser_task = False

    def classify(self, user_input: str) -> Tuple[str, str]:
        """
        Returns ("browser" | "pc" | "control", optional_goal).
        Uses fast keyword matching first; falls back to qwen2.5:1.5b only if ambiguous.
        """
        text = user_input.lower().strip()

        # Control commands always take priority
        if any(text.startswith(s) for s in STOP_COMMANDS):
            return "control", "stop"
        if any(text.startswith(p) for p in PAUSE_COMMANDS):
            return "control", "pause"
        if any(text.startswith(r) for r in RESUME_COMMANDS):
            return "control", "resume"

        # Fast PC-only path — never send these to browser
        pc_only = [
            "screenshot", "volume", "mute", "unmute", "lock", "sleep",
            "restart", "shutdown", "open app", "close app", "system info",
        ]
        if any(kw in text for kw in pc_only):
            return "pc", user_input

        # Fast keyword match for browser
        if any(kw in text for kw in BROWSER_KEYWORDS):
            return "browser", user_input

        # Let qwen2.5:1.5b classify ambiguous commands
        return self._llm_classify(user_input)

    def _llm_classify(self, user_input: str) -> Tuple[str, str]:
        prompt = (
            f"Classify this user request as either 'browser' or 'pc'.\n"
            f"Browser = anything involving web, search, websites, online shopping.\n"
            f"PC = open apps, files, volume, screenshot, system info.\n"
            f"Request: {user_input}\n"
            f"Respond with JSON only: {{\"type\": \"browser\"}} or {{\"type\": \"pc\"}}"
        )
        raw = generate_text(prompt=prompt, model=settings.FAST_MODEL, max_tokens=30)
        try:
            data = json.loads(raw.strip())
            task_type = data.get("type", "pc")
            return task_type, user_input
        except Exception:
            return "pc", user_input


# Singleton
_orchestrator: TaskOrchestrator = None


def get_orchestrator() -> TaskOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TaskOrchestrator()
    return _orchestrator
