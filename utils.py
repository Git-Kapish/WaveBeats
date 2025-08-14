"""
Utility classes: cooldown timer, hand history buffer.
"""

import time
from collections import deque

class ActionCooldown:
    def __init__(self, cooldown_ms: int = 1000):
        self.cooldown_ms = cooldown_ms
        self._last = 0

    def is_ready(self):
        return (time.time() * 1000) - self._last >= self.cooldown_ms

    def trigger(self):
        self._last = time.time() * 1000

class HandHistory:
    """
    Keeps a short history of palm-center x coordinates to detect swipe direction.
    Append None when no hand seen to keep timeline consistent.
    """
    def __init__(self, maxlen=8):
        self.history = deque(maxlen=maxlen)

    def append(self, x):
        # x is normalized or pixel coordinate (we use pixel in main)
        self.history.append(x)

    def clear(self):
        self.history.clear()
