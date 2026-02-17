"""
AppLib-core
======
Includes the essential components of AppLib, like configuration and logging..

Documentation is available in the docstrings.

:copyright: (c) 2026 by TheRealMorgenfrue.
:license: BSD 3-Clause
"""

from .configuration.config.config_base import ConfigBase
from .configuration.config.core_config import CoreConfig
from .configuration.internal.core_args import CoreArgs
from .configuration.runners.actions.theme_actions import (
    change_theme,
    change_theme_color,
)
from .configuration.runners.converters.cmd_converter import CMDConverter
from .configuration.runners.converters.color_converter import ColorConverter
from .configuration.runners.converters.converter import Converter
from .configuration.runners.converters.generic_converter import GenericConverter
from .configuration.runners.validators.app_validator import (
    validate_loglevel,
    validate_theme,
)
from .configuration.runners.validators.generic_validator import (
    validate_ip_address,
    validate_path,
    validate_proxy_address,
)
from .configuration.templates.base_template import BaseTemplate
from .configuration.templates.core_template import CoreTemplate
from .configuration.tools.cli_argument_gen import CLIArgumentGenerator
from .configuration.tools.config_tools import ConfigUtils
from .configuration.tools.config_utils.config_enums import ConfigLoadOptions
from .configuration.tools.ini_file_parser import IniFileParser
from .configuration.tools.search import SearchMode
from .configuration.tools.search.search_index import SEARCH_SEP
from .configuration.tools.template_parser import TemplateParser
from .configuration.tools.template_utils.groups import Group
from .configuration.tools.template_utils.options import (
    ColorPickerOption,
    ComboBoxOption,
    FileSelectorOption,
    GUIMessage,
    GUIOption,
    NumberOption,
    Option,
    TextEditOption,
)
from .configuration.tools.template_utils.template_enums import (
    UIFlags,
    UIGroups,
    UITypes,
)
from .configuration.tools.template_utils.validation_info import ValidationInfo
from .configuration.tools.validation_model_gen import (
    CoreValidationModelGenerator,
)
from .datastructures.trie import Trie
from .exceptions import IniParseError, InvalidMasterKeyError, MissingFieldError
from .logging import LoggingManager
from .types.config import AnyConfig
from .types.general import Model, StrPath
from .types.templates import AnyTemplate


__author__ = "TheRealMorgenfrue"

__all__ = [
    "AnyBoolSetting",
    "AnyCard",
    "AnyCardGenerator",
    "AnyCardGroup",
    "AnyCardStack",
    "AnyConfig",
    "AnyNestingCard",
    "AnyParentCard",
    "AnySetting",
    "AnySettingCard",
    "AnySettingWidget",
    "AnyTemplate",
    "AutoTextWrap",
    "BaseTemplate",
    "CardBase",
    "CardGenerator",
    "CardWidgetGenerator",
    "CMDConverter",
    "ColorConverter",
    "ColorPickerOption",
    "Converter",
    "ComboBoxOption",
    "CLIArgumentGenerator",
    "ClusteredSettingCard",
    "ClusteredSettingWidget",
    "ConfigBase",
    "ConfigLoadOptions",
    "ConfigUtils",
    "CoreArgs",
    "CoreConfig",
    "CoreTemplate",
    "ConsoleView",
    "CoreApp",
    "CoreHomeInterface",
    "CoreMainWindow",
    "CoreProcessInterface",
    "CoreSettingsInterface",
    "CoreSettingsSubInterface",
    "CoreStyleSheet",
    "CoreCheckBox",
    "CoreColorPicker",
    "CoreComboBox",
    "CoreFileSelect",
    "CoreLineEdit",
    "CoreSlider",
    "CoreSpinBox",
    "CoreSwitch",
    "CoreValidationModelGenerator",
    "Dialog",
    "ExpandingSettingCard",
    "FileSelectorOption",
    "FlowArea",
    "FlowSettingCard",
    "FluentLabel",
    "FluentSettingCard",
    "FormSettingCard",
    "GeneratorBase",
    "GeneratorUtils",
    "GenericConverter",
    "GenericSettingCard",
    "Group",
    "GUIMessage",
    "GUIOption",
    "iconDict",
    "IndeterminateProgressBarCard",
    "IndeterminateProgressRingCard",
    "InfoBar",
    "InfoBarPosition",
    "IniFileParser",
    "IniParseError",
    "InputView",
    "InvalidMasterKeyError",
    "LinkCard",
    "LinkCardView",
    "LoggingManager",
    "MenuListView",
    "MessageBoxBase",
    "MissingFieldError",
    "Model",
    "NestedSettingWidget",
    "NumberOption",
    "Option",
    "ParentCardBase",
    "PivotCardStack",
    "CoreProcessGUI",
    "ProcessGeneratorBase",
    "ProgressBarCard",
    "ProgressCard",
    "ProgressRingCard",
    "SampleCard",
    "SampleCardView",
    "SegmentedPivotCardStack",
    "SearchMode",
    "SettingCardBase",
    "SettingCardMixin",
    "SettingWidget",
    "SEARCH_SEP",
    "StrPath",
    "TemplateParser",
    "TextEditOption",
    "TextMessageBox",
    "ThreadManager",
    "ThreadManagerGui",
    "Trie",
    "UIFlags",
    "UIGroups",
    "UITypes",
    "ValidationInfo",
    "core_signalbus",
    "change_theme",
    "change_theme_color",
    "dict_lookup",
    "format_list_for_display",
    "format_validation_error",
    "iter_to_str",
    "validate_ip_address",
    "validate_loglevel",
    "validate_path",
    "validate_proxy_address",
    "validate_theme",
]
