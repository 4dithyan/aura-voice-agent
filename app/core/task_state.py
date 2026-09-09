"""app/core/task_state.py — Multi-step task memory."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class TaskState:
    goal: str
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    current_step: str = ""
    completed_steps: List[str] = field(default_factory=list)
    pending_steps: List[str] = field(default_factory=list)
    browser_state: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    last_results: List[Dict[str, Any]] = field(default_factory=list)
    requires_confirmation: bool = False
    confirmation_reason: str = ""
    is_cancelled: bool = False
    is_paused: bool = False
    step_count: int = 0

    def mark_step_done(self, step: str):
        self.completed_steps.append(step)
        self.step_count += 1

    def cancel(self):
        self.is_cancelled = True

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def to_summary(self) -> str:
        return (
            f"Goal: {self.goal} | "
            f"Step {self.step_count} | "
            f"Done: {', '.join(self.completed_steps[-3:]) or 'none'}"
        )
