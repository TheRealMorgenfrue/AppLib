"""
AppLib
======
An application component library for building small GUI apps easily.

Documentation is available in the docstrings.

:copyright: (c) 2025 by TheRealMorgenfrue.
:license: BSD 3-Clause
"""

import contextlib as __ctxl
import os
from pathlib import Path

# Set path for library code
os.environ["APPLIB_PATH"] = f"{Path(os.path.abspath(__file__)).parents[0]}"

# Dirty fix to silence noisy software
with __ctxl.redirect_stdout(None):
    from qfluentwidgets import QConfig as __silence

from .app.common.auto_wrap import AutoTextWrap
from .app.common.core_signalbus import core_signalbus
from .app.common.core_stylesheet import CoreStyleSheet
from .app.components.cardstack import PivotCardStack, SegmentedPivotCardStack
from .app.components.console_view import ConsoleView
from .app.components.dialogs.messagebox import TextMessageBox
from .app.components.dialogs.messagebox_base import Dialog, MessageBoxBase
from .app.components.flow_area import FlowArea
from .app.components.fluent_label import FluentLabel
from .app.components.infobar_test import InfoBar, InfoBarPosition
from .app.components.input_view import InputView
from .app.components.link_card import LinkCard, LinkCardView
from .app.components.menu_list_view import MenuListView
from .app.components.progresscards.progress_bar_card import (
    IndeterminateProgressBarCard,
    ProgressBarCard,
)
from .app.components.progresscards.progress_card import ProgressCard
from .app.components.progresscards.progress_ring_card import (
    IndeterminateProgressRingCard,
    ProgressRingCard,
)
from .app.components.sample_card import SampleCard, SampleCardView
from .app.components.settingcards.card_base import CardBase, ParentCardBase
from .app.components.settingcards.cards.clustered_settingcard import (
    ClusteredSettingCard,
)
from .app.components.settingcards.cards.expanding_settingcard import (
    ExpandingSettingCard,
)
from .app.components.settingcards.cards.settingcard import (
    FlowSettingCard,
    FluentSettingCard,
    FormSettingCard,
    GenericSettingCard,
    SettingCardBase,
    SettingCardMixin,
)
from .app.components.settingcards.widgets.parent_settingwidgets import (
    ClusteredSettingWidget,
    NestedSettingWidget,
)
from .app.components.settingcards.widgets.settingwidget import SettingWidget
from .app.components.settings import (
    CoreCheckBox,
    CoreColorPicker,
    CoreComboBox,
    CoreFileSelect,
    CoreLineEdit,
    CoreSlider,
    CoreSpinBox,
    CoreSwitch,
)
from .app.core_app import CoreApp
from .app.generators.card_generator import CardGenerator
from .app.generators.cardwidget_generator import CardWidgetGenerator
from .app.generators.generator_tools import GeneratorUtils
from .app.generators.generatorbase import GeneratorBase
from .app.interfaces.home_interface import CoreHomeInterface
from .app.interfaces.main_window import CoreMainWindow
from .app.interfaces.process.process_interface import CoreProcessInterface
from .app.interfaces.settings_interface import CoreSettingsInterface
from .app.interfaces.settings_subinterface import CoreSettingsSubInterface
from .module.concurrency.process.process_base import ProcessBase
from .module.concurrency.process.process_generator import ProcessGenerator
from .module.concurrency.process.stream_reader import asyncReadPipe
from .module.concurrency.thread.thread_manager import ThreadManager
from .module.concurrency.thread.thread_ui_streamer import ThreadUIStreamer
from .module.configuration.config.config_base import ConfigBase
from .module.configuration.config.core_config import CoreConfig
from .module.configuration.internal.core_args import CoreArgs
from .module.configuration.templates.base_template import BaseTemplate
from .module.configuration.templates.core_template import CoreTemplate
from .module.configuration.tools.config_tools import ConfigUtils
from .module.configuration.tools.ini_file_parser import IniFileParser
from .module.configuration.tools.template_options.groups import Group
from .module.configuration.tools.template_options.template_enums import (
    UIFlags,
    UIGroups,
    UITypes,
)
from .module.configuration.tools.template_options.validation_info import ValidationInfo
from .module.configuration.tools.template_parser import TemplateParser
from .module.configuration.tools.validation_model_gen import (
    CoreValidationModelGenerator,
)
from .module.configuration.validators import (
    validate_loglevel,
    validate_path,
    validate_theme,
)
from .module.datastructures.pure.meldableheap import MeldableHeap
from .module.datastructures.pure.redblacktree import RedBlackTree
from .module.datastructures.pure.yfasttrie import YFastTrie
from .module.datastructures.redblacktree_mapping import RedBlackTreeMapping
from .module.exceptions import IniParseError, InvalidMasterKeyError, MissingFieldError
from .module.logging import AppLibLogger, createLogger
from .module.tools.types.config import AnyConfig
from .module.tools.types.general import Model, StrPath, iconDict
from .module.tools.types.gui_cardgroups import AnyCardGroup
from .module.tools.types.gui_cards import (
    AnyCard,
    AnyNestingCard,
    AnyParentCard,
    AnySettingCard,
    AnySettingWidget,
)
from .module.tools.types.gui_generators import AnyCardGenerator
from .module.tools.types.gui_settings import AnyBoolSetting, AnySetting
from .module.tools.types.templates import AnyTemplate
from .module.tools.utilities import (
    checkDictNestingLevel,
    dictLookup,
    formatListForDisplay,
    formatValidationError,
    insertDictValue,
    iterToString,
    retrieveDictValue,
)
from .module.tools.version import VERSION

__author__ = "TheRealMorgenfrue"
__version__ = VERSION
__all__ = [
    "AnyBoolSetting",
    "AnyCard",
    "AnyCardGenerator",
    "AnyCardGroup",
    "AnyConfig",
    "AnyNestingCard",
    "AnyParentCard",
    "AnySetting",
    "AnySettingCard",
    "AnySettingWidget",
    "AnyTemplate",
    "AppLibLogger",
    "AutoTextWrap",
    "BaseTemplate",
    "CardBase",
    "CardGenerator",
    "CardWidgetGenerator",
    "ClusteredSettingCard",
    "ClusteredSettingWidget",
    "ConfigBase",
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
    "FlowArea",
    "FlowSettingCard",
    "FluentLabel",
    "FluentSettingCard",
    "FormSettingCard",
    "GeneratorBase",
    "GeneratorUtils",
    "GenericSettingCard",
    "Group",
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
    "MenuListView",
    "MeldableHeap",
    "MessageBoxBase",
    "MissingFieldError",
    "Model",
    "NestedSettingWidget",
    "ParentCardBase",
    "PivotCardStack",
    "ProcessBase",
    "ProcessGenerator",
    "ProgressBarCard",
    "ProgressCard",
    "ProgressRingCard",
    "RedBlackTree",
    "RedBlackTreeMapping",
    "SampleCard",
    "SampleCardView",
    "SegmentedPivotCardStack",
    "SettingCardBase",
    "SettingCardMixin",
    "SettingWidget",
    "StrPath",
    "TemplateParser",
    "TextMessageBox",
    "ThreadManager",
    "ThreadUIStreamer",
    "UIFlags",
    "UIGroups",
    "UITypes",
    "ValidationInfo",
    "asyncReadPipe",
    "core_signalbus",
    "createLogger",
    "dictLookup",
    "formatListForDisplay",
    "formatValidationError",
    "checkDictNestingLevel",
    "insertDictValue",
    "iterToString",
    "retrieveDictValue",
    "validate_loglevel",
    "validate_path",
    "validate_theme",
    "YFastTrie",
]
