"""app/browser/recovery.py — Retry logic and anti-loop fingerprinting."""
from __future__ import annotations
import hashlib
from typing import Dict


class RecoveryManager:
    """Tracks action fingerprints to detect and break retry loops."""

    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
        self._fingerprint_counts: Dict[str, int] = {}

    def fingerprint(self, action: str, target: str, args: str = "") -> str:
        return hashlib.md5(f"{action}:{target}:{args}".encode()).hexdigest()

    def should_retry(self, action: str, target: str, args: str = "") -> bool:
        fp = self.fingerprint(action, target, args)
        count = self._fingerprint_counts.get(fp, 0)
        if count >= self.max_retries:
            return False
        self._fingerprint_counts[fp] = count + 1
        return True

    def record_success(self, action: str, target: str, args: str = ""):
        fp = self.fingerprint(action, target, args)
        self._fingerprint_counts.pop(fp, None)

    def reset(self):
        self._fingerprint_counts.clear()
