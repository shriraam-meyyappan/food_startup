"""Bounded process-local throttling keyed by the ASGI client address."""

import math
from collections import deque
from collections.abc import Callable
from threading import Lock
from time import monotonic


class AuthRateLimiter:
    def __init__(self, limit: int, clock: Callable[[], float] = monotonic) -> None:
        self.limit = limit
        self.clock = clock
        self.events: dict[str, deque[float]] = {}
        self.lock = Lock()

    def retry_after(self, key: str) -> int | None:
        with self.lock:
            now = self.clock()
            for old_key in list(self.events):
                queue = self.events[old_key]
                while queue and queue[0] <= now - 60:
                    queue.popleft()
                if not queue:
                    del self.events[old_key]
            if key not in self.events and len(self.events) >= 4096:
                return 60
            queue = self.events.setdefault(key, deque())
            if len(queue) >= self.limit:
                return max(1, math.ceil(60 - (now - queue[0])))
            queue.append(now)
            return None
