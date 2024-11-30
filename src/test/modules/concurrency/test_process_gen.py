from typing import Any, Generator, override
from applib.module.concurrency.process.process_base import ProcessBase
from applib.module.concurrency.process.process_generator import ProcessGenerator
from test.modules.concurrency.test_process import TestProcess


class TestProcessGenerator(ProcessGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.test_size = 50

    @override
    def generator(self) -> Generator[ProcessBase, Any, Any]:
        for i in range(self.test_size):
            yield TestProcess()

    @override
    def canStart(self) -> bool:
        return self.test_size > 0

    @override
    def getTotalProgress(self) -> int:
        return self.test_size