from PyQt6.QtCore import QObject, pyqtSignal


class CoreSignalBus(QObject):
    # ───────────────────────────────────────────────────────────────────────────#
    # Config updates
    # ───────────────────────────────────────────────────────────────────────────#
    configStateChange = pyqtSignal(bool, str, str)
    """
    Notify whether a value was inserted in a config successfully or not.

    Parameters
    ----------
    is_success : bool
        The value was succesfully inserted in the config.

    title : str
        Title of GUI message.

    content : str
        Content of GUI message.
    """

    configUpdated = pyqtSignal(str, str, tuple, tuple)
    """
    Notify that a value in a config is updated.

    Parameters
    ----------
    config_name : str
        The name of the config.

    config_key : str
        The key whose value was updated.

    parent_key : tuple[str | None]
        The parent key of `config_key`.

    value : tuple[Any]
        The updated value mapped to `config_key`.
    """

    configNameUpdated = pyqtSignal(str, str)
    """
    Notify that the name of a config is updated.

    Parameters
    ----------
    old_config_name : str
        The old config name.

    new_config_name : str
        The new config name.
    """

    doSaveConfig = pyqtSignal(str)
    """
    Force the config to be saved to disk.

    Parameters
    ----------
    config_name : str
        The name of the config.
    """

    # ───────────────────────────────────────────────────────────────────────────#
    # Setting updates
    # ───────────────────────────────────────────────────────────────────────────#
    updateConfigSettings = pyqtSignal(str, str, tuple, tuple)
    """
    Update a key's value programmatically both in config and GUI.

    NOTE: Before emitting, it is required to have instantiated at least one GUI representation of a config using any Generator.

    Parameters
    ----------
    config_name : str
        The name of the config.

    config_key : str
        The key whose value should be updated.

    parent_key : tuple[str | None]
        The parent key of `config_key`.

    value : tuple[Any]
        The updated value mapped to `config_key`.
    """

    # ───────────────────────────────────────────────────────────────────────────#
    # Errors
    # ───────────────────────────────────────────────────────────────────────────#
    genericError = pyqtSignal(str, str)
    """
    Notify the user that a generic program error has occurred.

    Parameters
    ----------
    title : str
        Title of GUI message.

    content : str
        Content of GUI message.
    """

    configValidationError = pyqtSignal(str, str, str)
    """
    Notify the user that a config validation error occured.

    Parameters
    ----------
    config_name : str
        The name of the config.

    title : str
        Title of GUI message.

    content : str
        Content of GUI message.
    """

    # ───────────────────────────────────────────────────────────────────────────#
    # General
    # ───────────────────────────────────────────────────────────────────────────#
    isProcessesRunning = pyqtSignal(bool)
    """
    Notify whether processes are running in a ThreadManager.

    NOTE: Deprecated and scheduled for removal.

    Parameters
    ----------
    isRunning : bool
    """


core_signalbus = CoreSignalBus()
