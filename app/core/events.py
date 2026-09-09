"""app/core/events.py — Lightweight event emitter for live status updates."""
from typing import Callable, Dict, List, Any
from datetime import datetime


class EventEmitter:
    """Simple synchronous event bus. Attach listeners; browser agent fires events."""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self.history: List[Dict[str, Any]] = []

    def on(self, event: str, callback: Callable):
        self._listeners.setdefault(event, []).append(callback)

    def emit(self, event: str, **data):
        payload = {"event": event, "timestamp": datetime.now().isoformat(), **data}
        self.history.append(payload)
        # Keep history bounded
        if len(self.history) > 50:
            self.history = self.history[-50:]

        for cb in self._listeners.get(event, []):
            try:
                cb(payload)
            except Exception as e:
                print(f"[Events] Listener error for {event}: {e}")

        # Always print to terminal for visibility
        _print_event(payload)


def _print_event(payload: Dict[str, Any]):
    event = payload.get("event", "")
    ts = payload.get("timestamp", "")[:19]
    details = {k: v for k, v in payload.items() if k not in ("event", "timestamp")}
    detail_str = " | ".join(f"{k}={v}" for k, v in details.items()) if details else ""
    print(f"[{ts}] [{event}] {detail_str}")


# Global emitter instance
emitter = EventEmitter()
