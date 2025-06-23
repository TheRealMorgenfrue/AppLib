from modules.config.test_config import TestConfig

from applib.app.interfaces.home_interface import CoreHomeInterface


class TestHomeInterface(CoreHomeInterface):
    def __init__(self, parent=None):
        super().__init__(TestConfig(), parent)
