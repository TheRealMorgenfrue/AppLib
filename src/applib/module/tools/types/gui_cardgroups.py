from typing import TypeAlias

from ....app.components.settingcards.cards.scroll_settingcardgroup import (
    ScrollSettingCardGroup,
)
from ....app.components.settingcards.widgets.cardwidgetgroup import CardWidgetGroup


AnyCardGroup: TypeAlias = ScrollSettingCardGroup | CardWidgetGroup
