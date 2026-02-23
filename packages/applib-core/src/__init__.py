"""
AppLib-core
======
Includes the essential components of AppLib, like configuration and logging..

Documentation is available in the docstrings.

:copyright: (c) 2026 by TheRealMorgenfrue.
:license: BSD 3-Clause
"""

from .common.core_signalbus import core_signalbus
from .configuration.config.config_base import ConfigBase
from .configuration.config.core_config import CoreConfig
from .configuration.internal.core_args import CoreArgs
from .configuration.runners.converters.cmd_converter import CMDConverter
from .configuration.runners.converters.converter import Converter
from .configuration.runners.converters.generic_converter import GenericConverter
from .configuration.runners.validators.generic_validator import (
    validate_ip_address,
    validate_path,
    validate_proxy_address,
)
from .configuration.runners.validators.logging_validator import (
    validate_loglevel,
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
    AppLibUndefined,
    Option,
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
from .utilities import decodeInput
from .utilities.formatting import format_list_for_display, format_validation_error

__author__ = "TheRealMorgenfrue"

__all__ = [
    # Common
    "core_signalbus",
    # Configuration
    ## Config
    "ConfigBase",
    "CoreConfig",
    ## Internal
    "CoreArgs",
    ## Runners
    "CMDConverter",
    "Converter",
    "GenericConverter",
    "validate_ip_address",
    "validate_loglevel",
    "validate_path",
    "validate_proxy_address",
    ## Templates
    "BaseTemplate",
    "CoreTemplate",
    ## Tools
    "AppLibUndefined",
    "CLIArgumentGenerator",
    "ConfigLoadOptions",
    "ConfigUtils",
    "CoreValidationModelGenerator",
    "Group",
    "IniFileParser",
    "Option",
    "SearchMode",
    "SEARCH_SEP",
    "TemplateParser",
    "UIFlags",
    "UIGroups",
    "UITypes",
    "ValidationInfo",
    # Datastructures
    "Trie",
    # Exceptions
    "IniParseError",
    "InvalidMasterKeyError",
    "MissingFieldError",
    # Logging
    "LoggingManager",
    # Types
    "AnyConfig",
    "AnyTemplate",
    "Model",
    "StrPath",
    # Utilities
    "decodeInput",
    "format_list_for_display",
    "format_validation_error",
]
