import os

from qfluentwidgets import FluentIconBase, getIconColor, Theme
from enum import Enum

from ...module.configuration.internal.core_args import CoreArgs

# Example of creating custom widgets

# class CustomFluentIcon(FluentIconBase, Enum):
#     PIXIV = "Pixiv"
#     PIXIVFANBOX = "PixivFanbox"
#     FFMPEG = "FFmpeg"
#     DEBUG = "Debug"
#     IRFANVIEW = "Irfanview"
#     SHIELDPERSON = "ShieldPerson"
#     MEMBER = "FluentCollections16Regular"

#     def path(self, theme=Theme.AUTO) -> str:
#         # getIconColor() return "white" or "black" according to current theme
#         return f"{AppArgs.asset_icon_dir}{os.sep}{self.value}_{getIconColor(theme)}.svg"
