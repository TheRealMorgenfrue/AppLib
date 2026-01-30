from typing import override

from applib.module.concurrency.process.process_logger import CoreProcessLogger

from ...logging import LoggingManager


class CoreProcessGUI(CoreProcessLogger):
    """A process streaming its output to the GUI"""

    # TODO: LoggingManager for now. Make some abstract class or something
    def __init__(self, pid: int, program: str, args: str, logger: LoggingManager):
        super().__init__(pid=pid, program=program, args=args, logger=logger)

    @override
    def log_stdout(self, msg):
        self.process_logger.info(msg, log=False, pid=self.pid)

    @override
    def log_stderr(self, msg):
        self.process_logger.error(msg, log=False, pid=self.pid)
