from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    qps: Optional[float] = None
    qpm: Optional[float] = None
    output_file: str = "output.jsonl"
    num_workers: int = 4
    total_tasks: int = 100

    def __post_init__(self):
        if self.qps is not None and self.qpm is not None:
            raise ValueError("Specify either qps or qpm, not both.")

        if self.qps is not None and self.qps <= 0:
            raise ValueError("QPS must be positive.")
        if self.qpm is not None and self.qpm <= 0:
            raise ValueError("QPM must be positive.")

