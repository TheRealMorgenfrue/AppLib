from test.modules.config.test_args import TestArgs
from typing import Self, override

from applib import BaseTemplate, UIGroups, UITypes


class ProcessTemplate(BaseTemplate):
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._created = False
        return cls._instance

    def __init__(self) -> None:
        if not self._created:
            super().__init__(
                name=TestArgs.process_template_name,
                template=self._createTemplate(),
                icons=None,
            )
            self._created = True

    @override
    def _createTemplate(self) -> dict:
        return {
            "Process": {
                "maxThreads": {
                    "ui_title": f"Maxmimum number of threads to run concurrently",
                    "ui_desc": "Going beyond CPU core count will hurt performance for CPU-bound tasks",
                    "default": 1,
                    "min": 1,
                    "max": None,
                    "ui_group_parent": UIGroups.CLUSTERED,
                    "ui_group": "pu_threads",
                },
                "terminalSize": {
                    "ui_title": "Terminal size",
                    "ui_desc": "Set the size of the terminal in pixels",
                    "default": 600,
                    "min": 400,
                    "max": None,
                    "ui_type": UITypes.SPINBOX,
                    "ui_group": "pu_threads",
                },
            }
        }
