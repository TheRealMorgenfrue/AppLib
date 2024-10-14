import logging

from pathlib import Path
from datetime import datetime
from typing import Self

from .coloredformatter import ColoredFormatter
from .colorcodefilter import ColorCodeFilter
from ..config.internal.app_args import AppArgs
from ..config.tools.ini_file_parser import IniFileParser
from ..tools.utilities import retrieveDictValue


class Logger:
    _instance = None

    _logger_name = AppArgs.app_name
    _config_path = AppArgs.app_config_path
    _log_dir = AppArgs.log_dir
    _log_format = AppArgs.log_format
    _log_format_color = AppArgs.log_format_color
    _log_levels = AppArgs.template_loglevels

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._create_logger(
                cls._instance._getConfigLoglevel(cls._config_path)
            )
            cls._instance._create_logger_title()
            cls._instance._writeHeaderToLog()
        return cls._instance

    def _current_datetime(self) -> str:
        # return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return datetime.now().strftime("%Y-%m-%d")

    def _create_logger(self, level: str = "INFO") -> logging.Logger:
        self.logger = logging.getLogger(self._logger_name)
        self.logger.propagate = False
        self.logger.setLevel(level)

        console_handler = logging.StreamHandler()
        console_formatter = ColoredFormatter(self._log_format_color)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        if not self._log_dir.exists():
            self._log_dir.mkdir()
        file_handler = logging.FileHandler(
            f"{self._log_dir}/{self._current_datetime()}.log",
            encoding="utf-8",
        )
        file_formatter = ColorCodeFilter(self._log_format)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        return self.logger

    def _create_logger_title(self, level: str = "INFO") -> logging.Logger:
        self.logger_title = logging.getLogger(f"{self._logger_name}_title")
        self.logger_title.propagate = False
        self.logger_title.setLevel(level)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(message)s")
        console_handler.setFormatter(console_formatter)
        self.logger_title.addHandler(console_handler)

        if not self._log_dir.exists():
            self._log_dir.mkdir()
        file_handler = logging.FileHandler(
            f"{self._log_dir}/{self._current_datetime()}.log",
            encoding="utf-8",
        )
        file_formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(file_formatter)
        self.logger_title.addHandler(file_handler)

        return self.logger_title

    def _writeHeaderToLog(self) -> None:
        padding = 90
        header = (
            "┌"
            + "─" * padding
            + "┐"
            + "\n"
            + "│"
            + f"Starting application".center(padding, " ")
            + "│"
            + "\n"
            + "└"
            + "─" * padding
            + "┘"
        )
        self.logger_title.info(f"\n{header}")

    def _getConfigLoglevel(self, configpath: Path, default: str = "DEBUG") -> str:
        try:
            with open(configpath, "r", encoding="utf-8") as file:
                config = IniFileParser.load(
                    file
                )  # TODO: Make getting log level from config more robust (e.g. handle arbitrary config types)
        except FileNotFoundError:
            return default

        level = retrieveDictValue(config, "loglevel", default=default)  # type: str
        return level.strip('"')

    def get_logger(self) -> logging.Logger:
        return self.logger
