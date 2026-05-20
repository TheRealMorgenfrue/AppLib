from PyQt6.QtCore import QObject, pyqtSignal


class CoreSignalBus(QObject):
    # ───────────────────────────────────────────────────────────────────────────#
    # Config updates
    # ───────────────────────────────────────────────────────────────────────────#
    configUpdated = pyqtSignal(tuple, str, tuple, str)
    """
    Notify that a value in a config is updated.

    Parameters
    ----------
    names : tuple[str, str]
        [0]: The name of the config.
        [1]: The name of the template.

    config_key : str
        The key whose value was updated.

    value : tuple[Any]
        The updated value mapped to `config_key`.

    path : str
        The path of `config_key`
        May be relative or absolute.
        Paths are separated by forward slash, e.g. `Path/to/some/place`.
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

    # ───────────────────────────────────────────────────────────────────────────#
    # Setting updates
    # ───────────────────────────────────────────────────────────────────────────#
    updateConfigSettings = pyqtSignal(str, str, tuple, str)
    """
    Update a key's value programmatically both in config and GUI.

    NOTE: Before emitting, it is required to have instantiated at least one GUI representation of a config using any Generator.

    Parameters
    ----------
    config_name : str
        The name of the config.

    config_key : str
        The key whose value should be updated.

    value : tuple[Any]
        The updated value mapped to `config_key`.

    path : str
        The parent keys of `config_key`.
    """


core_signalbus = CoreSignalBus()
