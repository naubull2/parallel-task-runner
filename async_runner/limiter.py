import asyncio
import time

class TokenBucket:
    """An asyncio-compatible Token Bucket for rate limiting"""
    def __init__(self, rate: float, capacity: float):
        self.rate = rate
        self.capacity = capacity
        self._tokens = capacity
        self._last_refill_time = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            while self._tokens < 1:
                self._refill()
                await asyncio.sleep(max(0, (1 - self._tokens) / self.rate))
            self._tokens -= 1

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill_time
        if elapsed > 0:
            new_tokens = elapsed * self.rate
            self._tokens = min(self.capacity, self._tokens + new_tokens)
            self._last_refill_time = now
