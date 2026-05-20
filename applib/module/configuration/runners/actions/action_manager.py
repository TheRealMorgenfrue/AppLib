from collections.abc import Callable
from typing import Any

from .....app.common.core_signalbus import core_signalbus


class Actions:
    def __init__(self):
        pass

    def _onConfigUpdated(
        self,
        names: tuple[str, str],
        key: str,
        value_tuple: tuple[Any,],
        path: str,
        setting: str,
        action: Callable,
        parents: str,
        template_name: str,
    ):
        if key == setting and f"{path}" == f"{parents}" and names[1] == template_name:
            action(value_tuple[0])

    def add_action(
        self, setting: str, action: Callable, action_path: str, template_name: str
    ):
        core_signalbus.configUpdated.connect(
            lambda names, key, value_tuple, path: self._onConfigUpdated(
                names,
                key,
                value_tuple,
                path,
                setting,
                action,
                action_path,
                template_name,
            )
        )
