import json
from typing import Any, List, Tuple

import aiofiles


class InMemoryWriter:
    """Collects results in memory. Suitable for smaller datasets."""
    def __init__(self):
        self.successes: List[Any] = []
        self.failures: List[Tuple[Any, str]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def write_success(self, result: Any):
        self.successes.append(result)

    async def write_failure(self, failure: Tuple[Any, str]):
        self.failures.append(failure)


class ResultStreamWriter:
    """Asynchronously writes results to success and failure files in JSONL format."""
    def __init__(self, success_path: str, failure_path: str):
        self._success_path = success_path
        self._failure_path = failure_path
        self._success_file = None
        self._failure_file = None

    async def __aenter__(self):
        self._success_file = await aiofiles.open(self._success_path, 'w')
        self._failure_file = await aiofiles.open(self._failure_path, 'w')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._success_file:
            await self._success_file.close()
        if self._failure_file:
            await self._failure_file.close()

    async def write_success(self, result: Any):
        line = json.dumps(result) + '\n'
        await self._success_file.write(line)

    async def write_failure(self, failure: Tuple[Any, str]):
        task_input, error_msg = failure
        line = json.dumps({"input": task_input, "error": error_msg}) + '\n'
        await self._failure_file.write(line)

