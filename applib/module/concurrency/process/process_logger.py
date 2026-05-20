import asyncio
from typing import IO, Any, override

from applib.module.concurrency.process.process_base import CoreProcess

from ...logging import LoggingManager


class CoreProcessLogger(CoreProcess):
    """A process streaming its output to a logger"""

    # TODO: LoggingManager for now. Make some abstract class or something
    def __init__(self, pid: int, program: str, args: str, logger: LoggingManager):
        super().__init__(pid=pid, program=program, args=args)
        self.process_logger = logger

    async def _read_pipe(self) -> None:
        """
        Reads piped stdout/stderr from the process, line by line, in realtime.

        Important
        ---------
            Remember to disable buffering for the process.
            Otherwise stdout/stderr will only be shown upon process completion.
        """
        pending = {
            asyncio.create_task(
                self.process.stdout.readline(),
                name="stdout",
            ),
            asyncio.create_task(
                self.process.stderr.readline(),
                name="stderr",
            ),
        }
        while len(pending) > 0:
            done, pending = await asyncio.wait(
                pending, return_when=asyncio.FIRST_COMPLETED
            )
            for task in done:
                line = await task

                # If the line is empty, we are at the end of the stream
                if len(line) == 0:
                    continue

                # Re-create a readline() task for the respective stream
                match task.get_name():
                    case "stdout":
                        self.log_stdout(line.decode(errors="replace"))
                        pending.update(
                            (
                                asyncio.create_task(
                                    self.process.stdout.readline(), name="stdout"
                                ),
                            )
                        )
                    case "stderr":
                        self.log_stderr(line.decode(errors="replace"))
                        pending.update(
                            (
                                asyncio.create_task(
                                    self.process.stderr.readline(), name="stderr"
                                ),
                            )
                        )
        self.pipe_closed.emit()

    def log_stdout(self, msg: str):
        """Logs messages from stdout of the process.
        By default, `msg` is logged with level INFO to a log file.

        Reimplement to change logging behavior.
        """
        self.process_logger.info(msg)

    def log_stderr(self, msg: str):
        """Logs messages from stderr of the process.
        By default, `msg` is logged with level ERROR to a log file.

        Reimplement to change logging behavior.
        """
        self.process_logger.error(msg)

    @override
    async def process_monitor(self):
        await self._read_pipe()

    @override
    def stdout(self) -> int | IO[Any] | None:
        return asyncio.subprocess.PIPE

    @override
    def stderr(self) -> int | IO[Any] | None:
        return asyncio.subprocess.PIPE
