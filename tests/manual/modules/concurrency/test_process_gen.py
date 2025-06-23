import sys
from collections.abc import Generator
from pathlib import Path
from typing import Any, override

from modules.concurrency.test_process import TestProcess

from applib.module.concurrency.process.process_generator import ProcessGenerator


class TestProcessGenerator(ProcessGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.test_size = 50

    @override
    def program(self) -> str:
        return sys.executable

    @override
    def args(self) -> Generator[list[str], Any, Any]:
        for i in range(self.test_size):
            yield [
                f"{Path(r"src\test\modules\concurrency\test_file_program.py").resolve()}"
            ]

    @override
    def process(self) -> type[TestProcess]:
        return TestProcess

    @override
    def can_start(self) -> bool:
        return self.test_size > 0

    @override
    def get_total_progress(self) -> int:
        return self.test_size
