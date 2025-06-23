from typing import TypeAlias

from ....app.components.settings.checkbox import CoreCheckBox
from ....app.components.settings.color_picker import CoreColorPicker
from ....app.components.settings.combobox import CoreComboBox
from ....app.components.settings.file_selection import CoreFileSelect
from ....app.components.settings.line_edit import CoreLineEdit
from ....app.components.settings.slider import CoreSlider
from ....app.components.settings.spinbox import CoreSpinBox
from ....app.components.settings.switch import CoreSwitch

AnySetting: TypeAlias = (
    CoreColorPicker
    | CoreComboBox
    | CoreFileSelect
    | CoreLineEdit
    | CoreSlider
    | CoreSpinBox
    | CoreSwitch
    | CoreCheckBox
)

AnyBoolSetting: TypeAlias = CoreSwitch | CoreCheckBox
