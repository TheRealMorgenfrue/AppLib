from typing import TypeAlias

from app.components.settingcards.cards.clustered_settingcard import (
    ClusteredSettingCard,
)
from app.components.settingcards.cards.expanding_settingcard import (
    ExpandingSettingCard,
)
from app.components.settingcards.cards.settingcard import GenericSettingCard
from app.components.settingcards.widgets.settingwidget import SettingWidget
from app.components.settingcards.widgets.parent_settingwidgets import (
    ClusteredSettingWidget,
    NestedSettingWidget,
)


AnyCard: TypeAlias = (
    ExpandingSettingCard
    | ClusteredSettingCard
    | GenericSettingCard
    | NestedSettingWidget
    | ClusteredSettingWidget
    | SettingWidget
)

AnyParentCard: TypeAlias = (
    ExpandingSettingCard
    | ClusteredSettingCard
    | GenericSettingCard
    | NestedSettingWidget
    | ClusteredSettingWidget
)

AnyNestingCard: TypeAlias = ExpandingSettingCard | NestedSettingWidget

AnySettingCard: TypeAlias = (
    ExpandingSettingCard | ClusteredSettingCard | GenericSettingCard
)

AnySettingWidget: TypeAlias = (
    NestedSettingWidget | ClusteredSettingWidget | SettingWidget
)
