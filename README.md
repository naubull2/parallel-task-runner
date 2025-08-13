# parallel-task-runner

This script provides a high-performance, asyncio-based solution for running a large number of I/O-bound tasks (e.g., API calls) while maintaining strict control over the submission rate (QPS) and maximum concurrency via Token Bucket algorithm.

## Key Features

- **Strict QPS Control:** Utilizes a Token Bucket algorithm to enforce a hard ceiling on the number of tasks started per second. This is crucial for respecting API rate limits.
- **High Concurrency:** Built on `asyncio` for memory-efficient handling of thousands of concurrent operations.
- **Fail-Safe Operation:** Includes automatic retries with exponential backoff for tasks that fail due to trasient errors.
- **Lossless Processing:** Tasks that fail all retry attempts are collected and reported at the end, ensuring no input is silently lost.

## When to Use It

This module is particularly useful for:

- Interacting with third-party APIs that have strict rate limits.
- Batch-processing a large dataset against a web service.
- Running web scraping tasks in a controlled and respectful manner.
- Any high-volume, I/O-bound operation that needs to be throttled to prevent system overload.

## Installation
```bash
cd parallel-task-runner
poetry install
```

## Usage

The package's primary entry point is shown in the [demo.py](./demo.py) script. You can configure the run using the following arguments.

**Basic Example:**

```bash
# Run 1000 tasks with a max QPS of 50 and max concurrency of 100
python demo.py --tasks 1000 --qps 50 --concurrency 100
```

**Control Log Verbosity**

To see detailed debug messages, such as retry attempts for failed takss, set the log level to `DEBUG`

```bash
python demo.py --log-level DEBUG
```


# Contributing

Contributions are welcom! Please submit a pull request with your changes.

