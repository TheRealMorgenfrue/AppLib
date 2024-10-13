from typing import TypeAlias

from app.components.settings.checkbox import ConfigCheckBox
from app.components.settings.color_picker import ConfigColorPicker
from app.components.settings.combobox import ConfigComboBox
from app.components.settings.line_edit import ConfigLineEdit
from app.components.settings.slider import ConfigSlider
from app.components.settings.spinbox import ConfigSpinBox
from app.components.settings.switch import ConfigSwitch

AnySetting: TypeAlias = (
    ConfigColorPicker
    | ConfigComboBox
    | ConfigLineEdit
    | ConfigSlider
    | ConfigSpinBox
    | ConfigSwitch
    | ConfigCheckBox
)

AnyBoolSetting: TypeAlias = ConfigSwitch | ConfigCheckBox
