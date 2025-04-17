from concurrent.futures import ThreadPoolExecutor
import time
import queue
import json
from typing import Any, Dict
from threading import Lock
import threading

from parallel_task_runner.config import Config
from parallel_task_runner.worker import WorkerTask


class TaskManager:
    def __init__(self, config: Config, worker: WorkerTask):
        self.config = config
        self.worker = worker
        self.output_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=self.config.num_workers)

        self.start_time = time.time()
        self.completed_tasks = 0
        self.lock = Lock()

    def submit_task(self, task_data: Any):
        return self.executor.submit(self._process_task, task_data)


    def _process_task(self, task_data: Any):
        self.rate_limit()
        try:
            result = self.worker.execute(task_data)
            self.output_queue.put(result)
        except Exception as e:
            print(f"Error processing task: {e}")
            self.output_queue.put({"error": str(e), "task_data": task_data})
        finally:
            with self.lock:
                self.completed_tasks += 1

    def rate_limit(self):
        if self.config.qps:
            elapsed_time = time.time() - self.start_time
            target_time = self.completed_tasks / self.config.qps
            sleep_time = target_time - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)
        elif self.config.qpm:
            elapsed_time = time.time() - self.start_time
            target_time = self.completed_tasks / (self.config.qpm / 60)
            sleep_time = target_time - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    def write_output_to_file(self): 
        while True:
            try:
                result = self.output_queue.get(timeout=1)
                self.worker.write_output(result, self.config.output_file)
                self.output_queue.task_done()
            except queue.Empty:
                if self.executor._shutdown:
                    break

    def shutdown(self):
        self.executor.shutdown(wait=True)
        self.output_queue.join()
        
