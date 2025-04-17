import time
import threading

from parallel_task_runner.config import Config
from parallel_task_runner.worker import WorkerTask
from parallel_task_runner.manager import TaskManager


def main():
    config = Config(qps=20, output_file="results.jsonl", num_workers=10, total_tasks=200)

    class MyWorker(WorkerTask):
        def execute(self, task_data):
            time.sleep(0.01)
            return {"result": f"Processed {task_data}", "timestamp": time.time()}


    worker = MyWorker()
    task_manager = TaskManager(config, worker)

    futures = []
    for i in range(config.total_tasks):
        futures.append(task_manager.submit_task(f"Task {i}"))

    output_thread = threading.Thread(target=task_manager.write_output_to_file)
    output_thread.daemon = True
    output_thread.start()

    task_manager.shutdown()
    print("All tasks completed")


if __name__=="__main__":
    main()

