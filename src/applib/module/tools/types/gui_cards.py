from ....app.components.settingcards.cards.clustered_settingcard import (
    ClusteredSettingCard,
)
from ....app.components.settingcards.cards.expanding_settingcard import (
    ExpandingSettingCard,
)
from ....app.components.settingcards.cards.settingcard import GenericSettingCard
from ....app.components.settingcards.widgets.parent_settingwidgets import (
    ClusteredSettingWidget,
    NestedSettingWidget,
)
from ....app.components.settingcards.widgets.settingwidget import SettingWidget

type AnyCard = (
    ExpandingSettingCard
    | ClusteredSettingCard
    | GenericSettingCard
    | NestedSettingWidget
    | ClusteredSettingWidget
    | SettingWidget
)

type AnyParentCard = (
    ExpandingSettingCard
    | ClusteredSettingCard
    | GenericSettingCard
    | NestedSettingWidget
    | ClusteredSettingWidget
)

type AnyNestingCard = ExpandingSettingCard | NestedSettingWidget

type AnySettingCard = ExpandingSettingCard | ClusteredSettingCard | GenericSettingCard

type AnySettingWidget = NestedSettingWidget | ClusteredSettingWidget | SettingWidget
