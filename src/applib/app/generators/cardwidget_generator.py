from typing import override

from PyQt6.QtWidgets import QWidget

from ...module.configuration.tools.template_utils.groups import Group
from ...module.configuration.tools.template_utils.options import GUIOption
from ...module.configuration.tools.template_utils.template_enums import (
    UIGroups,
    UITypes,
)
from ...module.tools.types.config import AnyConfig
from ...module.tools.types.gui_cards import AnySettingWidget
from ...module.tools.types.templates import AnyTemplate
from ..components.settingcards.widgets.cardwidgetgroup import CardWidgetGroup
from ..components.settingcards.widgets.parent_settingwidgets import (
    ClusteredSettingWidget,
    NestedSettingWidget,
)
from ..components.settingcards.widgets.settingwidget import SettingWidget
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


class CardWidgetGenerator(GeneratorBase):
    def __init__(
        self,
        config: AnyConfig,
        template: AnyTemplate,
        default_group: str | None = None,
        hide_group_label: bool = True,
        is_tight: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        """
        Generate a Setting Card Widget for each setting in the supplied template.
        The type of the Setting Card Widget depends on various factors, including a setting's relation to other settings.

        The CardWidget generator is very useful for templates consisting only of nested UIGroups.

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
            parent=parent,
        )
        self._cards = self._generate_cards(CardWidgetGroup)

    @override
    def _create_card(
        self,
        card_type: UITypes,
        setting: str,
        option: GUIOption,
        path: str,
        group: Group | None,
        parent: QWidget | None = None,
    ) -> AnySettingWidget | None:
        widget = None
        try:
            is_nesting_group = (
                group
                and setting == group.get_parent_name()
                and UIGroups.NESTED_CHILDREN in group.get_ui_group_parent()
            )
            is_clustered_group = (
                group
                and setting == group.get_parent_name()
                and UIGroups.CLUSTERED in group.get_ui_group_parent()
            )
            if is_nesting_group and card_type == UITypes.SWITCH:
                card_type = UITypes.CHECKBOX

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
            # Create Setting Card Widget
            if is_nesting_group:
                card = NestedSettingWidget(
                    card_name=setting,
                    title=option.ui_info.title,
                    content=option.ui_info.description,
                    has_disable_button=has_disable_button,
                    parent=parent,
                )
            elif is_clustered_group:
                card = ClusteredSettingWidget(
                    card_name=setting,
                    title=option.ui_info.title,
                    content=option.ui_info.description,
                    has_disable_button=has_disable_button,
                    parent=parent,
                )
            else:
                card = SettingWidget(
                    card_name=setting,
                    title=option.ui_info.title,
                    content=option.ui_info.description,
                    has_disable_button=has_disable_button,
                    parent=parent,
                )
            card.set_option(widget)
            return card
        except Exception:
            if widget:
                widget.deleteLater()
            raise
