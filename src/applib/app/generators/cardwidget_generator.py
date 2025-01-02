from PyQt6.QtWidgets import QWidget
from typing import Any, Optional, override


from ..components.settingcards.widgets.cardwidgetgroup import CardWidgetGroup
from ..components.settingcards.widgets.settingwidget import SettingWidget
from ..components.settingcards.widgets.parent_settingwidgets import (
    ClusteredSettingWidget,
    NestedSettingWidget,
)
from .generatorbase import GeneratorBase

from ...module.config.templates.template_enums import UIGroups, UITypes
from ...module.config.tools.template_options.groups import Group
from ...module.tools.types.config import AnyConfig
from ...module.tools.types.gui_cards import AnySettingWidget
from ...module.tools.types.templates import AnyTemplate

"""
Explanation of terms:
    setting = A key which influences some decision in the program.
              Equivalent to a line in the config file or the GUI element created from said config.
              For instance, the setting for the line 'loglevel = "DEBUG"' in a config is 'loglevel'.

    option  = A child key of a setting in the Template.
              For instance, the setting "loglevel" contains a child key "default"
              (specifying the default value for "loglevel").
"""


class CardWidgetGenerator(GeneratorBase):
    def __init__(
        self,
        config: AnyConfig,
        template: AnyTemplate,
        default_group: Optional[str] = None,
        hide_group_label: bool = True,
        is_tight: bool = False,
        config_name_override: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Generate a Setting Card Widget for each setting in the supplied template.
        The type of the Setting Card Widget depends on various factors, including a setting's relation to other settings.

        The CardWidget generator is very useful for templates consisting only of any `UIGroups` nested parent/child relationships.

        Parameters
        ----------
        config : ConfigBase
            The config object from which cards receive/store their values.

        template : AnyTemplate
            The template which cards are created from.
            The config should originate from the same template.

        default_group : str, optional
            The card group which is displayed on app start.
            By default `None`.

        hide_group_label : bool, optional
            Hide the name of the card group.
            Usually, some other GUI element takes care of displaying this.
            By default `True`.

        is_tight : bool, optional
            Use a smaller version of the setting widgets, if available.

        config_name_override : str | None, optional,
            Override the default config name with this string.
            Used for error message display.

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
            config_name_override=config_name_override,
            parent=parent,
        )
        self._cards = self._generateCards(CardWidgetGroup)

    @override
    def _createCard(
        self,
        card_type: UITypes,
        setting: str,
        options: dict[str, Any],
        content: str,
        group: Group | None,
        parent: Optional[QWidget] = None,
    ) -> AnySettingWidget | None:
        widget = None
        try:
            isNestingGroup = (
                group
                and setting == group.getParentName()
                and UIGroups.NESTED_CHILDREN in group.getUIGroupParent()
            )
            isClusteredGroup = (
                group
                and setting == group.getParentName()
                and UIGroups.CLUSTERED in group.getUIGroupParent()
            )
            if isNestingGroup and card_type == UITypes.SWITCH:
                card_type = UITypes.CHECKBOX

            title = options["ui_title"]
            has_disable_button = "ui_disable_self" in options
            if "disable_button" in options:
                has_disable_button = options["disable_button"]  # type: bool

            # Create Setting
            widget = self._createSetting(
                card_type=card_type,
                setting_name=setting,
                options=options,
                parent=parent,
            )
            # Create Setting Card Widget
            if isNestingGroup:
                card = NestedSettingWidget(
                    setting=setting,
                    title=title,
                    content=content,
                    hasDisableButton=has_disable_button,
                    parent=parent,
                )
            elif isClusteredGroup:
                card = ClusteredSettingWidget(
                    setting=setting,
                    title=title,
                    content=content,
                    hasDisableButton=has_disable_button,
                    parent=parent,
                )
            else:
                card = SettingWidget(
                    setting=setting,
                    title=title,
                    content=content,
                    hasDisableButton=has_disable_button,
                    parent=parent,
                )
            card.setOption(widget)
            return card
        except Exception:
            if widget:
                widget.deleteLater()
            raise
