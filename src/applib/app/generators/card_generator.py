from typing import Any, Optional, Union, override

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import FluentIconBase

from ...module.configuration.tools.template_options.groups import Group
from ...module.configuration.tools.template_options.template_enums import (
    UIGroups,
    UITypes,
)
from ...module.tools.types.config import AnyConfig
from ...module.tools.types.gui_cards import AnySettingCard
from ...module.tools.types.templates import AnyTemplate
from ..components.settingcards.cards.clustered_settingcard import ClusteredSettingCard
from ..components.settingcards.cards.expanding_settingcard import ExpandingSettingCard
from ..components.settingcards.cards.scroll_settingcardgroup import (
    ScrollSettingCardGroup,
)
from ..components.settingcards.cards.settingcard import FluentSettingCard
from .generatorbase import GeneratorBase

"""
Explanation of terms:
    setting = A key which influences some decision in the program.
              Equivalent to a line in the config file or the GUI element created from said config.
              For instance, the setting for the line 'loglevel = "DEBUG"' in a config is 'loglevel'.

    option  = A child key of a setting in the Template.
              For instance, the setting "loglevel" contains a child key "default"
              (specifying the default value for "loglevel").
"""


class CardGenerator(GeneratorBase):
    def __init__(
        self,
        config: AnyConfig,
        template: AnyTemplate,
        default_group: Optional[str] = None,
        hide_group_label: bool = True,
        is_tight: bool = False,
        icons: Optional[list[Union[str, QIcon, FluentIconBase]]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Generate a Setting Card for each setting in the supplied template.
        The type of the Setting Card depends on various factors, including a setting's relation to other settings.

        The Setting Card generator is useful for general-purpose templates containing a bit of everything.
        However, the Setting Cards might not look well in confined space, even with `is_tight`, so keep that in mind.

        Parameters
        ----------
        config : ConfigBase
            The config object from which cards receive/store their values.

        template : AnyTemplate
            The template which cards are created from.
            The config should originate from the same template.

        default_group : str, optional
            The name of the section card group which is displayed on application start.
            By default `None`.

        hide_group_label : bool, optional
            Hide the name of the card group.
            Usually, some other GUI element takes care of displaying this.
            By default `True`.

        is_tight : bool, optional
            Use a smaller version of the setting widgets, if available.

        icons : list[str | QIcon | FluentIconBase], optional
            Add an icon to each card generated.
            By default `None`.

        parent : QWidget, optional
            The parent of all card groups generated.
            By default `None`.
        """
        super().__init__(
            config=config,
            template=template,
            default_group=default_group,
            hide_group_label=hide_group_label,
            is_tight=is_tight,
            parent=parent,
        )
        self._icons = icons if icons else FIF.LEAF
        self._cards = self._generateCards(ScrollSettingCardGroup)

    @override
    def _createCard(
        self,
        card_type: UITypes,
        setting: str,
        options: dict[str, Any],
        parent_keys: list[str],
        content: str,
        group: Group | None,
        parent: Optional[QWidget] = None,
    ) -> AnySettingCard | None:
        widget = None
        try:
            if isinstance(self._icons, list):
                icon = self._icons.pop(0)
            else:
                icon = self._icons

            isNestingGroup = (
                group and UIGroups.NESTED_CHILDREN in group.getUIGroupParent()
            )
            isClusteredGroup = group and UIGroups.CLUSTERED in group.getUIGroupParent()

            title = options["ui_title"]
            has_disable_button = "ui_disable_self" in options
            if "disable_button" in options:
                has_disable_button = options["disable_button"]  # type: bool

            # Create Setting
            widget = self._createSetting(
                card_type=card_type,
                key=setting,
                options=options,
                parent_keys=parent_keys,
                parent=parent,
            )
            # Create Setting Card
            if isNestingGroup and setting == group.getParentName():
                card = ExpandingSettingCard(
                    card_name=setting,
                    icon=icon,
                    title=title,
                    content=content,
                    has_disable_button=has_disable_button,
                    parent=parent,
                )
            elif isClusteredGroup and setting == group.getParentName():
                card = ClusteredSettingCard(
                    card_name=setting,
                    icon=icon,
                    title=title,
                    content=content,
                    has_disable_button=has_disable_button,
                    parent=parent,
                )
            else:
                card = FluentSettingCard(
                    card_name=setting,
                    icon=icon,
                    title=title,
                    content=content,
                    has_disable_button=has_disable_button,
                    is_frameless=isNestingGroup,
                    parent=parent,
                )
            card.enableTightMode(self._is_tight)
            card.setOption(widget)
            return card
        except Exception:
            if widget:
                widget.deleteLater()
            raise
