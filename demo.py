import asyncio
import time
import random
import logging
import argparse
from typing import Dict

from async_runner import AsyncQPSAwareRunner, InMemoryWriter, ResultStreamWriter


async def sample_api_call(task_id: int) -> Dict:
    """A sample async worker that simulates a network call with possible failure"""
    if random.random() < 0.10:
        raise ConnectionError("Transient network error")
    await asyncio.sleep(random.uniform(0.01, 0.05))
    return {"task_id": task_id, "status": "success"}


async def main():
    parser = argparse.ArgumentParser(description="A scalable, async batch processor with QPS limiting.")
    parser.add_argument("--tasks", type=int, default=1000, help="Total number of tasks to run.")
    parser.add_argument("--qps", type=int, default=100, help="Maximum queries per second.")
    parser.add_argument("--concurrency", type=int, default=100, help="Maximum concurrent tasks.")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries for a filed task.")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Set the logging level.")

    # Streaming mode options
    parser.add_argument("--stream", action="store_true", help="Enable streaming results to files instead of storing in memory.")
    parser.add_argument("--success-file", type=str, default="success.jsonl", help="File to store successful results (in stream mode).")
    parser.add_argument("--failure-file", type=str, default="failure.jsonl", help="File to store failed tasks (in stream mode).")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    logging.info(f"Starting runner with configuration: {args}")

    # Choose the writer based on the flag
    writer = ResultStreamWriter(args.success_file, args.failure_file) if args.stream else InMemoryWriter()

    async with writer:
        runner = AsyncQPSAwareRunner(
            async_worker=sample_api_call,
            writer=writer,
            max_qps=args.qps,
            max_concurrency=args.concurrency,
            retries=args.retries,
        )
        
        start_time = time.time()
        success_count, failure_count = await runner.run(range(args.tasks))
        total_time = time.time() - start_time

        final_qps = success_count / total_time if total_time > 0 else 0
        logging.info("--- JOB COMPLETE ---")
        logging.info(f"Processed {args.tasks} tasks in {total_time:.2f} seconds.")
        logging.info(f"  Final Average QPS: {final_qps:.2f}")
        logging.info(f"  Successful: {success_count}")
        logging.info(f"  Failed: {failure_count}")

        if args.stream:
            logging.info(f"Results saved to {args.success_file} and {args.faillure_file}")
        else:
            if writer.failures:
                logging.warning("Sample of failed tasks (input, error):")
                for task, error in writer.failures[:5]:
                    logging.warning(f"    - Task: {task}, Error: {error}")
        logging.info("--------------------")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("\nProcess interrupted by user. Exiting gracefully.")


