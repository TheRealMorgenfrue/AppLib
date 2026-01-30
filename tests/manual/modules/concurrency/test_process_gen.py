import sys
from itertools import repeat
from pathlib import Path
from typing import override

from applib.module.concurrency.process.process_generator import ProcessGeneratorBase


class TestProcessGenerator(ProcessGeneratorBase):
    def __init__(self) -> None:
        super().__init__()
        self.test_size = 50

    @override
    def program(self) -> str:
        return sys.executable

    @override
    def arguments_list(self):
        arg = f"{Path(r"tests/manual/modules/concurrency/test_file_program.py").resolve()}"
        return list(repeat(arg, self.test_size))
