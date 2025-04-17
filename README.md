# parallel-task-runner

A Python boilerplate for running IO bound tasks in parallel with controlled queries per second (QPS) or 
queries per minute (QPM). This is usefull for scenarios where you need to process a large number of tasks
such as making external API calls or systems while respecting the imposed rate limits.

## Features
 * **Rate Limiting:** Control the execution rate using either QPS or QPM.
 * **Parallel Execution:** Utilize multiple worker threads for efficient task processing.
 * **Modular Design:** Easily define and an plug in your own task logic.
 * **JSONL Output:** Write task results to a JSONL file (one JSON object per line) for easy analysis and storage.
 * **Error Handling:** Gracefully handles exceptions during task execution and logs errors to the output file.
 * **Configurable:** Configure the task runner using a simple dataclass.

## Installation
```bash
cd parallel-task-runner
poetry install
```

## Usage

Define your task: Create a class that inherits from `parallel_task_runner.worker.WorkerTask` and
implement the `execute` method to perform your specific task. The `execute` method should accept task data
as input and return a dictionary containing the results.

Refer to the following sample code.
[./my_script.py](./my_script.py)
 
```python
from parallel_task_runner.config import Config
from parallel_task_runner.worker import WorkerTask
form parallel_task_runner.manager import TaskManager

import time # used to simulate IO bound task

class MyTask(WorkerTask):
    def execute(self, task_data):
        # Define your task
        time.sleep(0.1)
        return {"result": f"Processed: {task_data}"}

config = Config(qps=10, output_file="results.jsonl", num_workers=4, total_tasks=100)

my_task = MyTask()

task_data = [f"Task {i}" for i in range(config.total_tasks)]
for data in task_data:
    task_manager.submit_task(data)

task_manager.run()
print("All tasks completed")
```

## Configuration

The `Config` dataclass allows you to configure the task runner. Here's a description of the available options:

- `qps` (float, optional) : Queries per second. If specified, QPM is ignored.
- `qpm` (float, optioanl) : Queries per minute. If specified, QPS is ignored.
- `output_file` (str) : The path to the output JSONL file.
- `num_workers` (int) : The number of worker threads to use.
- `total_tasks` (int) : The total number of tasks to run (demonstration purpose only)

# Contributing

Contributions are welcom! Please submit a pull request with your changes.

