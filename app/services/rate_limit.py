from time import time
from collections import defaultdict


class RateLimiter:
    def __init__(
        self,
        max_attempts: int,
        window_seconds: int,
    ):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = defaultdict(list)

    def allow(self, key: str) -> bool:

        now = time()

        attempts = self.attempts[key]

        attempts[:] = [t for t in attempts if now - t < self.window_seconds]

        if len(attempts) >= self.max_attempts:
            return False

        attempts.append(now)

        return True
