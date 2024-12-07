from time import time
import traceback
from typing import Any, Mapping

from ...app.common.core_signalbus import core_signalbus

from .internal.core_args import CoreArgs
from .tools.config_tools import (
    checkMissingFields,
    loadConfig,
    validateValue,
    writeConfig,
)
from ..logging import logger
from ..tools.types.general import Model, StrPath
from ..tools.utilities import retrieveDictValue


class ConfigBase:
    """Base class for all configs"""

    _logger = logger

    def __init__(
        self,
        template_model: dict[str, Any],
        validation_model: Model,
        config_name: str,
        config_path: StrPath,
        save_interval: int = 1,
    ) -> None:
        """
        Initiate config wrapper class.

        Parameters
        ----------
        template : dict[str, Any]
            A dict created from a `Model`, resembling a template,
            from which the config will be created.

        validation_model : Model
            The model used to validate the config.
            The type is a Pydantic model.

        config_name : str
            The name of the config to create.

        config_path : StrPath
            The config's location on disk.

        save_interval : int, optional
            Time between config saves in seconds, by default 1.
        """
        self._load_failure = False  # The config failed to load
        self._is_modified = False  # A modified config needs to be written to disk
        self._save_interval = save_interval  # Time between config saves in seconds
        self._last_save_time = (
            time()
        )  # Prevent excessive disk writing (with multiple write requests in a short time span)
        self._config_name = config_name
        self._config_path = config_path
        self._config = None  # type: dict[str, Any]
        self._template_model = template_model
        self._validation_model = validation_model
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self) -> None:
        core_signalbus.configNameUpdated.connect(self._onConfigNameUpdated)
        core_signalbus.doSaveConfig.connect(self._onSaveConfig)

    def _onConfigNameUpdated(self, old_name: str, new_name: str) -> None:
        if old_name == self._config_name:
            self._config_name = new_name

    def _onSaveConfig(self, config_name: str) -> None:
        if self._config_name == config_name:
            self.saveConfig()

    def _initConfig(self) -> dict[str, Any]:
        """Loads the config from a file.

        This is the default implementation.
        To change its behavior, simply @override this method in a subclass.

        Returns
        -------
        dict[str, Any]
            The loaded config.
        """
        config, self._load_failure = loadConfig(
            config_name=self._config_name,
            config_path=self._config_path,
            validator=self._validateLoad,
            template=self._template_model,
        )
        return config

    def _validateLoad(self, raw_config: Mapping) -> dict[str, Any]:
        """Validates the config when loaded from a file.

        This is the default implementation.
        To change its behavior, simply @override this method in a subclass.

        Parameters
        ----------
        raw_config : dict
            The raw, unvalidated config loaded from a file.

        Returns
        -------
        dict[str, Any]
            The validated config.
        """
        validated_config = self._validation_model.model_validate(raw_config)
        config = validated_config.model_dump()
        checkMissingFields(raw_config, config)
        return config

    def _validate(self, save_config: dict[str, Any], *args) -> None:
        """Validates the config when a value is changed,
        ensuring only valid values exists at any given time.

        This is the default implementation.
        To change its behavior, simply @override this method in a subclass.

        Parameters
        ----------
        config : dict[str, Any]
            The config to validate
        """
        self._config = self._validation_model.model_validate(save_config).model_dump()

    def _setConfig(self, config: dict[str, Any]) -> None:
        self._config = config

    def setTemplateConfig(self, template_config: dict[str, Any]) -> None:
        self._template_model = template_config

    def setValidationModel(self, validation_model: Model) -> None:
        self._validation_model = validation_model

    def getConfig(self) -> dict[str, Any]:
        """
        Get the config's underlying dict.

        Returns
        -------
        dict[str, dict]
            The config's underlying dict
        """
        return self._config

    def getConfigName(self) -> str:
        return self._config_name

    def getFailureStatus(self) -> bool:
        """
        Returns whether the config failed to load.

        Returns
        -------
        bool
            True == failed (i.e. the config is not usable).
        """
        return self._load_failure

    def setFailureStatus(self, status: bool) -> None:
        self._load_failure = status

    def getValue(
        self, key: str, default: Any = None, use_template: bool = False
    ) -> Any:
        """
        Get a value from the config dictionary object.
        Return first value found. If there is no item with that key, return default.

        This is the default implementation.
        To change its behavior, simply @override this method in a subclass.

        Note: the dictionary is usually nested. Thus, the "get" method of a Python dict
        is insufficient to retrieve all values.

        Parameters
        ----------
        key : str
            The dictionary key to search for (i.e. the config setting)

        default : Any, optional
            Return default value if the key is not found. By default None.

        use_template : bool, optional
            Use the template config, by default False.
            The template config is useful for getting e.g. default values of settings.

        Returns
        -------
        Any
            The value of the key if found, else the default value.
        """
        config = self._template_model if use_template else self._config
        value = retrieveDictValue(d=config, key=key, default=default)
        if value is None:
            self._logger.warning(
                f"Config '{self._config_name}': Could not find key '{key}' in the config. Returning default: '{default}'"
            )
        return value

    def setValue(self, key: str, value: Any, config_name: str) -> bool:
        """
        Update the config dictionary with `value`.

        Parameters
        ----------
        key : str
            The dictionary key to search for (i.e. the config setting).

        value : Any
            The value to insert.

        config_name : str
            The name of the config.

        Returns
        -------
        bool
            Whether the config was validated successfully with the new *value*.
            True == invalid (i.e. the value was NOT saved).
        """
        isError, isInvalid = validateValue(
            config_name=config_name,
            config=self._config,
            validator=self._validate,
            setting=key,
            value=value,
        )
        if isError:
            core_signalbus.configStateChange.emit(False, "Failed to save setting", "")
        else:
            core_signalbus.configUpdated.emit(config_name, key, (value,))
            self._is_modified = True
        return isInvalid

    def saveConfig(self) -> None:
        """Write config to disk"""
        try:
            if (
                self._is_modified
                and (self._last_save_time + self._save_interval) < time()
            ):
                self._last_save_time = time()
                writeConfig(self._config, self._config_path)
                self._is_modified = False
        except Exception:
            msg = "Failed to save the config"
            self._logger.error(
                f"Config '{self._config_name}': {msg}\n"
                + traceback.format_exc(limit=CoreArgs.traceback_limit)
            )
            core_signalbus.configStateChange.emit(False, msg, "")
