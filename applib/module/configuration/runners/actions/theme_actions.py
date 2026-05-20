from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from qfluentwidgets import Theme, setTheme, setThemeColor


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
