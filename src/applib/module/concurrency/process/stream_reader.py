import asyncio
from typing import Optional

from PyQt6.QtCore import pyqtBoundSignal


async def async_read_pipe(
    process: asyncio.subprocess.Process,
    stdout: pyqtBoundSignal,
    stderr: Optional[pyqtBoundSignal] = None,
) -> None:
    """
    Reads piped stdout from *process*, line by line, in realtime.

    Important
    ---------
        Remember to disable buffering for the *process*.\n
        Otherwise stdout will only be shown upon process completion (i.e. when returning to caller)

    Parameters
    ----------
    process : Popen (Must be an asyncio Popen process!)
        The subprocess to read stdout from

    streamSignal : pyqtBoundSignal
        Signal to send stdout data to
    """
    pending = {
        asyncio.create_task(
            process.stdout.readline(),
            name="stdout",
        ),
        # asyncio.create_task(
        #     process.stderr.readline(),
        #     name="stderr",
        # ),
    }
    while len(pending) > 0:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            name = task.get_name()
            line = await task

            # If the line is empty, we are at the end of the stream
            if len(line) == 0:
                continue

            stdout.emit(line.decode(errors="replace"))

            # Re-create a readline() task for a respective stream
            if task.get_name() == "stdout":
                pending.update(
                    (
                        asyncio.create_task(process.stdout.readline(), name="stdout"),
                        # asyncio.create_task(process.stderr.readline(), name="stderr"),
                    )
                )
