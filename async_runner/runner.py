import asyncio
import logging
from typing import Any, Coroutine, Iterable, Tuple

from tqdm.asyncio import tqdm
from .limiter import TokenBucket


class AsyncQPSAwareRunner:
    """Processes async tasks with QPS and concurrency control, using a provided writer."""
    def __init__(self, 
                 async_worker: Coroutine,
                 writer: Any,
                 max_qps: float,
                 max_concurrency: int,
                 retries: int = 3):
        self.async_worker = async_worker
        self.writer = writer
        self.max_qps = float(max_qps)
        self.max_concurrency = max_concurrency
        self.retries = retries

        self.limiter = TokenBucket(rate=self.max_qps, capacity=self.max_qps)
        self.semaphore = asyncio.Semaphore(max_concurrency)

        self.success_count = 0
        self.failure_count = 0

    async def _worker_wrapper(self, task: Any):
        await self.limiter.acquire()
        async with self.semaphore:
            last_exception = None
            for attempt in range(self.retries + 1):
                try:
                    if attempt > 0:
                        logging.debug(f"Retrying task (attempt {attempt+1}/{self.retries+1})...")
                    result = await self.async_worker(task)
                    await self.writer.write_success(result)
                    self.success_count += 1
                    return
                except Exception as e:
                    last_exception = e
                    logging.debug(f"Task failed on attempt {attempt+1}: {e}")
                    await asyncio.sleep(0.5 * (2 ** attempt))
            if last_exception:
                await self.writer.write_failure((task, str(last_exception)))
                self.failure_count += 1

    async def run(self, input_source: Iterable[Any]) -> Tuple[int, int]:
        self.success_count = 0
        self.failure_count = 0
        tasks = [asyncio.create_task(self._worker_wrapper(item)) for item in input_source]
        await tqdm.gather(*tasks, desc=f"Processing Tasks (QPS: {self.max_qps}, Concurrency: {self.max_concurrency})")
        return self.success_count, self.failure_count
