from modules.concurrency.test_process_gen import TestProcessGenerator
from modules.config.templates.process_template import ProcessTemplate
from modules.config.test_config import TestConfig
from PyQt6.QtWidgets import QWidget

from applib.app.interfaces.process.process_interface import CoreProcessInterface
from applib.module.concurrency.thread.thread_manager_gui import ThreadManagerGui


class TestProcessInterface(CoreProcessInterface):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            TestConfig(),
            ProcessTemplate(),
            TestProcessGenerator,
            ThreadManagerGui,
            parent,
        )
