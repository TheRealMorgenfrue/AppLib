from applib.module.config.core_config import CoreConfig
from applib.module.config.templates.core_template import CoreTemplate
from qfluentwidgets import FluentIcon as FIF

from applib.app.interfaces.main_window import CoreMainWindow
from test.interfaces.home import TestHomeInterface
from test.interfaces.process import TestProcessInterface
from test.interfaces.settings import TestSettingsInterface


class TestMainWindow(CoreMainWindow):
    def __init__(self):
        super().__init__(
            main_config=CoreConfig(),
            main_template=CoreTemplate(),
            subinterfaces=[
                (TestHomeInterface, FIF.HOME, "Home"),
                (TestProcessInterface, FIF.IOT, "Process"),
            ],
            settings_interface=(TestSettingsInterface, FIF.SETTING, "Settings"),
            app_icon=FIF.AIRPLANE.qicon(),
        )
