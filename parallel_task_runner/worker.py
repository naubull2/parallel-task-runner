import json
from abc import ABC, abstractmethod
from typing import Any, Dict


class WorkerTask(ABC):
    @abstractmethod
    def execute(self, task_data: Any) -> Dict:
        pass

    def write_output(self, result: Dict, output_file: str):
        with open(output_file, "a") as f:
            print(json.dumps(result, ensure_ascii=False), file=f)

