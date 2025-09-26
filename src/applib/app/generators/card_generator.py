from typing import override

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import FluentIconBase

from ...module.configuration.tools.template_utils.groups import Group
from ...module.configuration.tools.template_utils.options import GUIOption
from ...module.configuration.tools.template_utils.template_enums import (
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
        default_group: str | None = None,
        hide_group_label: bool = True,
        is_tight: bool = False,
        blank_path=False,
        icons: list[str | QIcon | FluentIconBase] | None = None,
        parent: QWidget | None = None,
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
            By default None.

        hide_group_label : bool, optional
            Hide the name of the card group.
            Usually, some other GUI element takes care of displaying this.
            By default True.

        is_tight : bool, optional
            Use a smaller version of the setting widgets, if available.
            By default False.

        blank_path : bool, optional
            Do not use paths when getting values from the config.
            This allows the config paths to differ from the template's.
            By default False.

        icons : list[str | QIcon | FluentIconBase], optional
            Add an icon to each card generated.
            By default None.

        parent : QWidget, optional
            The parent of all card groups generated.
            By default None.
        """
        super().__init__(
            config=config,
            template=template,
            default_group=default_group,
            hide_group_label=hide_group_label,
            is_tight=is_tight,
            blank_path=blank_path,
            parent=parent,
        )
        self._icons = icons if icons else FIF.LEAF
        self._cards = self._generate_cards(ScrollSettingCardGroup)

    @override
    def _create_card(
        self,
        card_type: UITypes,
        setting: str,
        option: GUIOption,
        path: str,
        group: Group | None,
        parent: QWidget | None = None,
    ) -> AnySettingCard | None:
        widget = None
        try:
            if isinstance(self._icons, list):
                icon = self._icons.pop(0)
            else:
                icon = self._icons

            is_nesting_group = (
                group and UIGroups.NESTED_CHILDREN in group.get_ui_group_parent()
            )
            is_clustered_group = (
                group and UIGroups.CLUSTERED in group.get_ui_group_parent()
            )

            has_disable_button = option.defined(option.ui_disable_self)
            if option.defined(option.ui_disable_button):
                has_disable_button = option.ui_disable_button

            # Create Setting
            widget = self._create_setting(
                card_type=card_type,
                key=setting,
                option=option,
                path=path,
                parent=parent,
            )
            # Create Setting Card
            if is_nesting_group and setting == group.get_parent_name():  # type: ignore
                card = ExpandingSettingCard(
                    card_name=setting,
                    icon=icon,
                    title=option.ui_info.title,
                    content=option.ui_info.description,
                    has_disable_button=has_disable_button,
                    parent=parent,
                )
            elif is_clustered_group and setting == group.get_parent_name():  # type: ignore
                card = ClusteredSettingCard(
                    card_name=setting,
                    icon=icon,
                    title=option.ui_info.title,
                    content=option.ui_info.description,
                    has_disable_button=has_disable_button,
                    parent=parent,
                )
            else:
                card = FluentSettingCard(
                    card_name=setting,
                    icon=icon,
                    title=option.ui_info.title,
                    content=option.ui_info.description,
                    has_disable_button=has_disable_button,
                    is_frameless=bool(is_nesting_group),
                    parent=parent,
                )
            card.enable_tight_mode(self._is_tight)
            card.set_option(widget)
            return card
        except Exception:
            if widget:
                widget.deleteLater()
            raise
