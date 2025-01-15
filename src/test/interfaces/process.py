from PyQt6.QtWidgets import QWidget
from applib.app.interfaces.process.process_interface import CoreProcessInterface
from applib.module.concurrency.thread.thread_ui_streamer import ThreadUIStreamer
from test.modules.concurrency.test_process_gen import TestProcessGenerator
from test.modules.config.templates.process_template import ProcessTemplate
from test.modules.config.test_config import TestConfig


class TestProcessInterface(CoreProcessInterface):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            TestConfig(),
            ProcessTemplate(),
            TestProcessGenerator,
            ThreadUIStreamer,
            parent,
        )
