import threading
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
        self.attempts: defaultdict[str, list[float]] = defaultdict(list)
        # Los endpoints son síncronos y corren en el threadpool de Starlette, así que
        # varias peticiones pueden tocar `attempts` a la vez: protegemos con un lock.
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:

        now = time()

        with self._lock:
            # Purga global de intentos caducados y de claves ya vacías, para que el
            # diccionario no crezca sin límite con el tiempo (una entrada por IP).
            for existing_key in list(self.attempts):
                timestamps = self.attempts[existing_key]
                timestamps[:] = [t for t in timestamps if now - t < self.window_seconds]
                if not timestamps:
                    del self.attempts[existing_key]

            attempts = self.attempts[key]

            if len(attempts) >= self.max_attempts:
                return False

            attempts.append(now)

            return True
