# Private AppLib module.

import logging

from ..configuration.internal.core_args import CoreArgs
from .logging_manager import LoggingManager


def create_basic_logger(name: str) -> logging.Logger:
    return LoggingManager().create_logger(
        name=name,
        level="INFO",
        use_color=False,
        log_dir=CoreArgs._core_log_dir,
        log_filename=CoreArgs._core_log_filename,
    )


def maybe_write_header_to_log() -> None:
    """Write startup header, if enabled"""
    if not CoreArgs._core_log_disable_header:
        logger_nocolor = create_basic_logger(f"{CoreArgs._core_log_name}_HEADER")
        padding = 90
        header = (
            "┌"
            + "─" * padding
            + "┐"
            + "\n"
            + "│"
            + "Starting application".center(padding, " ")
            + "│"
            + "\n"
            + "└"
            + "─" * padding
            + "┘"
        )
        logger_nocolor.info(f"\n{header}")
        LoggingManager().delete_logger(logger_nocolor.name)
