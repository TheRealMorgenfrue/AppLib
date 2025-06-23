from typing import Self, override

from modules.config.test_args import TestArgs

from applib import BaseTemplate, UIGroups, UITypes
from applib.module.configuration.tools.template_utils.options import (
    GUIMessage,
    NumberOption,
)


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
                template=self._create_template(),
                icons=None,
            )
            self._created = True

    @override
    def _create_template(self) -> dict:
        return {
            "Process": {
                "maxThreads": NumberOption(
                    default=1,
                    min=1,
                    max=None,
                    ui_group_parent=UIGroups.CLUSTERED,
                    ui_group="pu_threads",
                    ui_info=GUIMessage(
                        f"Maxmimum number of threads to run concurrently",
                        "Going beyond CPU core count will decrease performance for CPU-bound tasks",
                    ),
                ),
                "terminalSize": NumberOption(
                    default=600,
                    min=400,
                    max=None,
                    ui_group="pu_threads",
                    ui_info=GUIMessage(
                        "Terminal size", "Set the size of the terminal in pixels"
                    ),
                    ui_type=UITypes.SPINBOX,
                ),
            }
        }
