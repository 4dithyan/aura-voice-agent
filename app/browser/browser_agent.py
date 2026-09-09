"""app/browser/browser_agent.py — OBSERVE→PLAN→ACT→VERIFY loop."""
from __future__ import annotations
import json
from typing import Optional, List, Dict, Any

from app.browser.controller import get_controller, BrowserController
from app.browser.state import BrowserState
from app.browser.recovery import RecoveryManager
from app.browser.result_extractor import extract_search_results, summarize_results_for_voice
from app.browser.form_filler import fill_form
from app.vision.analyzer import find_element_visually
from app.agent.ollama_client import generate_text
from app.core.events import emitter
from app.core.task_state import TaskState
from app.config import settings

# ------------------------------------------------------------------ system prompt

BROWSER_PLANNER_SYSTEM = """You are a browser automation planner.
Given the current browser state and user goal, decide the SINGLE NEXT action.
Respond with a JSON object ONLY — no text, no markdown.

Available actions:
{"action": "navigate", "url": "https://..."}
{"action": "click", "target": "<button/link text or aria-label>"}
{"action": "fill", "field": "<field name or placeholder>", "value": "<value>"}
{"action": "press_key", "key": "<Enter|Tab|Escape|...>"}
{"action": "scroll", "direction": "down"}
{"action": "click_result", "index": <1-based number>}
{"action": "extract_results"}
{"action": "go_back"}
{"action": "wait", "seconds": 2}
{"action": "done", "message": "<short summary for user>"}
{"action": "ask_user", "question": "<what to ask>"}
{"action": "confirm_required", "reason": "<purchase|booking|destructive>", "detail": "<short detail>"}

Rules:
- Use "confirm_required" when reaching checkout, payment, or order placement.
- Use "ask_user" when you cannot determine the next action from the page state.
- Use "done" when the goal is fully accomplished.
- Output ONLY the JSON object. Nothing else.
"""


# ------------------------------------------------------------------ confirmation keywords

CONFIRMATION_PAGE_TYPES = {"checkout", "payment"}
CONFIRMATION_KEYWORDS = [
    "place order", "pay now", "confirm order", "complete purchase",
    "buy now", "proceed to pay", "confirm booking", "make payment",
]


class BrowserAgent:
    """Runs a multi-step browser task using the OBSERVE→PLAN→ACT→VERIFY loop."""

    def __init__(self):
        self.recovery = RecoveryManager(max_retries=settings.MAX_ACTION_RETRIES)
        self._task: Optional[TaskState] = None

    # ------------------------------------------------------------------ public

    def run_task(self, goal: str, user_request: str) -> str:
        """
        Executes a browser task end-to-end.
        Returns a voice-friendly response string.
        """
        self._task = TaskState(goal=goal)
        ctrl = get_controller()

        if not ctrl.is_open:
            if not ctrl.open():
                return "I couldn't open the browser."

        emitter.emit("task_started", goal=goal)

        for step_num in range(settings.MAX_TASK_STEPS):
            if self._task.is_cancelled:
                return "Task cancelled."
            if self._task.is_paused:
                return "Task paused. Say 'resume' to continue."

            # --- OBSERVE ---
            state = ctrl.get_page_state()
            self._task.browser_state = state.to_compact_dict(settings.MAX_CONTEXT_ITEMS)

            # Check for special page types immediately
            special = self._check_special_page(state)
            if special:
                return special

            # --- PLAN ---
            next_action = self._plan_next_action(goal, state, user_request)
            if not next_action:
                return "I wasn't sure what to do next. Please try again."

            action_type = next_action.get("action", "")

            # --- Handle terminal actions ---
            if action_type == "done":
                msg = next_action.get("message", "Task completed.")
                self._task.mark_step_done("done")
                emitter.emit("task_completed", message=msg)
                return msg

            if action_type == "ask_user":
                q = next_action.get("question", "What would you like me to do?")
                return q

            if action_type == "confirm_required":
                reason = next_action.get("reason", "purchase")
                detail = next_action.get("detail", "")
                return self._build_confirmation_request(reason, detail)

            # --- ACT ---
            success = self._execute_action(ctrl, state, next_action)
            step_label = f"{action_type}:{next_action.get('target', next_action.get('url', ''))}"
            self._task.mark_step_done(step_label)

            if not success:
                # Vision fallback
                if settings.VISION_ON_FAILURE and settings.VISION_ENABLED:
                    success = self._vision_fallback(ctrl, next_action)
                if not success:
                    # Re-plan from fresh page state
                    continue

        return "I reached the maximum steps for this task. Please try a simpler command."

    def cancel(self):
        if self._task:
            self._task.cancel()
        emitter.emit("task_cancelled")

    def pause(self):
        if self._task:
            self._task.pause()
        emitter.emit("task_paused")

    def resume(self):
        if self._task:
            self._task.resume()
        emitter.emit("task_resumed")

    # ------------------------------------------------------------------ private

    def _plan_next_action(
        self, goal: str, state: BrowserState, user_request: str
    ) -> Optional[Dict[str, Any]]:
        """Calls qwen2.5:1.5b to decide the next action. Returns parsed JSON or None."""
        compact_state = state.to_compact_dict(settings.MAX_CONTEXT_ITEMS)
        completed = self._task.completed_steps[-5:] if self._task else []

        max_tokens = 150 if settings.LOW_RESOURCE_MODE else 300

        prompt = (
            f"User request: {user_request}\n"
            f"Overall goal: {goal}\n"
            f"Current page: {compact_state.get('title', '')} | {compact_state.get('url', '')}\n"
            f"Page type: {compact_state.get('page_type', '')}\n"
            f"Visible buttons: {[b['text'] for b in compact_state.get('buttons', [])[:5]]}\n"
            f"Visible inputs: {[i['placeholder'] or i['name'] for i in compact_state.get('inputs', [])[:5]]}\n"
            f"Completed steps: {completed}\n"
            "What is the SINGLE NEXT action?"
        )

        raw = generate_text(
            prompt=prompt,
            system=BROWSER_PLANNER_SYSTEM,
            model=settings.FAST_MODEL,
            max_tokens=max_tokens,
        )

        return _parse_action(raw)

    def _execute_action(
        self, ctrl: BrowserController, state: BrowserState, action: Dict[str, Any]
    ) -> bool:
        """Executes a single browser action. Returns True on success."""
        a = action.get("action", "")
        target = action.get("target", "")
        args_str = json.dumps(action)

        if not self.recovery.should_retry(a, target, args_str):
            emitter.emit("action_blocked", action=a, reason="loop_detected")
            return False

        if a == "navigate":
            url = action.get("url", "")
            ok = ctrl.navigate(url)
            if ok:
                self.recovery.record_success(a, target)
            return ok

        elif a == "click":
            ok = ctrl.click(target)
            if ok:
                self.recovery.record_success(a, target)
            return ok

        elif a == "fill":
            field = action.get("field", "")
            value = action.get("value", "")
            ok = ctrl.fill(field, value)
            if ok:
                self.recovery.record_success(a, field)
            return ok

        elif a == "press_key":
            return ctrl.press_key(action.get("key", "Enter"))

        elif a == "scroll":
            return ctrl.scroll(action.get("direction", "down"))

        elif a == "click_result":
            idx = int(action.get("index", 1))
            return ctrl.click_nth_result(idx)

        elif a == "extract_results":
            results = extract_search_results(ctrl._page)
            if self._task:
                self._task.last_results = results
            summary = summarize_results_for_voice(results)
            emitter.emit("results_extracted", count=len(results))
            # We inject the summary as the task's done message
            action["action"] = "done"
            action["message"] = summary
            return True

        elif a == "go_back":
            return ctrl.go_back()

        elif a == "wait":
            import time
            time.sleep(float(action.get("seconds", 1)))
            return True

        return False

    def _vision_fallback(self, ctrl: BrowserController, failed_action: Dict[str, Any]) -> bool:
        """Takes a screenshot and asks qwen3-vl:4b to find the element."""
        emitter.emit("vision_analysis_started")
        shot = ctrl.screenshot()
        if not shot:
            return False

        target = failed_action.get("target", "") or failed_action.get("field", "")
        result = find_element_visually(shot, target)
        emitter.emit("vision_analysis_completed", found=bool(result.get("found", True)))

        if result.get("below_threshold") or result.get("found") is False:
            return False

        # If vision returned a region, use approximate center click
        region = result.get("approximate_region")
        if region and not result.get("below_threshold"):
            try:
                page = ctrl._page
                vp = page.viewport_size
                cx = int(region.get("x", 0.5) * vp["width"] + region.get("width", 0.1) * vp["width"] / 2)
                cy = int(region.get("y", 0.5) * vp["height"] + region.get("height", 0.1) * vp["height"] / 2)
                page.mouse.click(cx, cy)
                ctrl._wait_for_settle()
                return True
            except Exception:
                pass
        return False

    def _check_special_page(self, state: BrowserState) -> Optional[str]:
        """Checks for pages requiring special handling (captcha, login, checkout)."""
        if state.page_type == "captcha":
            emitter.emit("captcha_detected")
            return "A CAPTCHA requires your attention. Please solve it manually, then say 'resume'."

        if state.page_type == "login":
            emitter.emit("login_required")
            return "Login is required. Please complete the login manually, then say 'resume'."

        if state.page_type == "checkout":
            if settings.CONFIRM_PURCHASES:
                price = self._extract_price(state)
                emitter.emit("waiting_for_confirmation", reason="checkout", price=price)
                return self._build_confirmation_request("checkout", price)

        # Check visible text for confirmation keywords
        text_l = state.visible_text.lower()
        for kw in CONFIRMATION_KEYWORDS:
            if kw in text_l:
                if settings.CONFIRM_PURCHASES:
                    price = self._extract_price(state)
                    return self._build_confirmation_request("purchase", price)
                break

        return None

    def _build_confirmation_request(self, reason: str, detail: str) -> str:
        if reason == "checkout":
            return f"We're at the checkout page{'. Total: ' + detail if detail else ''}. Shall I continue? Say yes or no."
        if reason == "purchase":
            return f"I'm about to place an order{' for ' + detail if detail else ''}. Shall I continue? Say yes or no."
        return f"This action requires your confirmation: {detail}. Say yes to continue."

    def _extract_price(self, state: BrowserState) -> str:
        """Attempts to find a price in the visible text."""
        import re
        matches = re.findall(r"[₹$€£]\s?[\d,]+(?:\.\d{2})?", state.visible_text)
        return matches[0] if matches else ""


# ------------------------------------------------------------------ JSON parser

def _parse_action(raw: str) -> Optional[Dict[str, Any]]:
    """Parses LLM output into an action dict."""
    if not raw:
        return None
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict) and "action" in data:
            return data
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                data = json.loads(cleaned[start:end])
                if isinstance(data, dict) and "action" in data:
                    return data
            except Exception:
                pass
    return None


# ------------------------------------------------------------------ singleton

_agent: Optional[BrowserAgent] = None


def get_browser_agent() -> BrowserAgent:
    global _agent
    if _agent is None:
        _agent = BrowserAgent()
    return _agent
