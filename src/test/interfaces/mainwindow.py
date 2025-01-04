from applib.module.config.core_config import CoreConfig
from applib.module.config.internal.core_args import CoreArgs
from qfluentwidgets import FluentIcon as FIF

from applib.app.interfaces.main_window import CoreMainWindow
from test.interfaces.home import TestHomeInterface
from test.interfaces.process import TestProcessInterface
from test.interfaces.settings import TestSettingsInterface


class TestMainWindow(CoreMainWindow):
    def __init__(self):
        super().__init__(
            setup_args=CoreArgs,
            MainConfig=CoreConfig,
            subinterfaces=[
                (TestHomeInterface, FIF.HOME, "Home"),
                (TestProcessInterface, FIF.IOT, "Process"),
            ],
            settings_interface=(TestSettingsInterface, FIF.SETTING, "Settings"),
        )
