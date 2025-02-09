from typing import Any, Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from qfluentwidgets import Theme, setTheme, setThemeColor

from .....app.common.core_signalbus import core_signalbus


class Actions:
    def __init__(self):
        pass

    def _onConfigUpdated(
        self,
        names: tuple[str, str],
        key: str,
        value_tuple: tuple[Any,],
        parent_keys: list[str],
        setting: str,
        action: Callable,
        parents: list[str],
        template_name: str,
    ):
        if (
            key == setting
            and f"{parent_keys}" == f"{parents}"
            and names[1] == template_name
        ):
            action(value_tuple[0])

    def add_action(
        self, setting: str, action: Callable, parents: list[str], template_name: str
    ):
        core_signalbus.configUpdated.connect(
            lambda names, key, value_tuple, parent_keys: self._onConfigUpdated(
                names,
                key,
                value_tuple,
                parent_keys,
                setting,
                action,
                parents,
                template_name,
            )
        )


def change_theme(value: str):
    if value == "Light":
        theme = Theme.LIGHT
    elif value == "Dark":
        theme = Theme.DARK
    else:
        theme = Theme.AUTO
    setTheme(theme=theme, lazy=True)


def change_theme_color(color: QColor | Qt.GlobalColor | str):
    setThemeColor(color, lazy=True)
