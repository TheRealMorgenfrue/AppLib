from abc import abstractmethod
import traceback
from PyQt6.QtWidgets import QWidget
from typing import Any, Optional

from ..common.core_signalbus import core_signalbus
from ..components.settings.file_selection import CoreFileSelect
from ..components.settings.checkbox import CoreCheckBox
from ..components.settings.color_picker import CoreColorPicker
from ..components.settings.combobox import CoreComboBox
from ..components.settings.line_edit import CoreLineEdit
from ..components.settings.slider import CoreSlider
from ..components.settings.spinbox import CoreSpinBox
from ..components.settings.switch import CoreSwitch
from .generator_tools import (
    UIGrouping,
    inferType,
    parseUnit,
    updateCardGrouping,
)

from ...module.config.internal.core_args import CoreArgs
from ...module.config.templates.template_enums import UIFlags, UITypes
from ...module.config.tools.template_options.groups import Group
from ...module.config.tools.template_parser import TemplateParser
from ...module.logging import AppLibLogger
from ...module.tools.types.config import AnyConfig
from ...module.tools.types.gui_cardgroups import AnyCardGroup
from ...module.tools.types.gui_cards import AnyCard, AnySettingCard
from ...module.tools.types.gui_settings import AnySetting
from ...module.tools.types.templates import AnyTemplate
from ...module.tools.utilities import iterToString


class GeneratorBase:
    _logger = AppLibLogger().getLogger()

    def __init__(
        self,
        config: AnyConfig,
        template: AnyTemplate,
        default_group: Optional[str] = None,
        hide_group_label: bool = True,
        is_tight: bool = False,
        parent_key: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        if config.getFailureStatus():
            err_msg = f"Config '{config.getConfigName()}' is invalid"
            raise RuntimeError(err_msg)
        self._config = config
        self._template = template
        self._template_name = self._template.getName()
        self._config_name = parent_key if parent_key else config.getConfigName()
        self._default_group = default_group
        self._hide_group_label = hide_group_label
        self._is_tight = is_tight
        self._parent_key = parent_key
        self._parent = parent

        # type: dict[str, list] # Mapping of the correct card sort order.
        self._card_sort_order = {}
        # type: list[AnyCardGroup] # Temp placement of unsorted cards.
        self._card_list = []
        # type: list[AnyCardGroup] # The cards sorted correctly.
        self._cards = []

    @abstractmethod
    def _createCard(
        self,
        card_type: UITypes,
        setting: str,
        options: dict[str, Any],
        content: str,
        group: Group | None,
        parent: Optional[QWidget] = None,
    ) -> AnyCard | None:
        """
        Create a setting card to be displayed in the GUI.

        Parameters
        ----------
        card_type : UITypes
            The type of the card. See `UITypes` for card types.

        setting : str
            The setting this card represent.
            That is, a key in the template (and by extension, the config).

        options : dict[str, Any]
            Options detailing how the card should look and behave.
            That is, the value of `setting` in the template.

        content : str
            The description of the card.

        group : Group | None
            The group this card belongs to.
            Defines how this card is placed relative to other cards.

        parent : Optional[QWidget], optional
            The parent of the card.
            By default `None`.

        Returns
        -------
        AnyCard | None
            A setting card which can be displayed in a GUI.
        """
        ...

    def _createSetting(
        self,
        card_type: UITypes,
        setting_name: str,
        options: dict,
        parent: Optional[QWidget] = None,
    ) -> AnySetting | None:
        """
        Create setting widget for use on a setting card.

        Parameters
        ----------
        card_type : UITypes
            The type of the setting, e.g., Switch.

        setting_name : str
            The name of the setting, i.e., its ID/key in the config.

        options : dict
            The options available for this setting, e.g., its default value.

        parent : QWidget, optional
            The parent of this setting, by default `None`.

        Returns
        -------
        AnySetting | None
            The setting widget object if created succesfully, else `None`.
        """
        if card_type == UITypes.CHECKBOX:
            widget = CoreCheckBox(
                config=self._config,
                config_key=setting_name,
                options=options,
                parent_key=self._parent_key,
                parent=parent,
            )
        elif card_type == UITypes.COLOR_PICKER:
            widget = CoreColorPicker(
                config=self._config,
                config_key=setting_name,
                options=options,
                parent_key=self._parent_key,
                parent=parent,
            )
        elif card_type == UITypes.COMBOBOX:
            widget = CoreComboBox(
                config=self._config,
                config_key=setting_name,
                options=options,
                texts=options["values"],
                parent_key=self._parent_key,
                parent=parent,
            )
        elif card_type == UITypes.FILE_SELECTION:
            widget = CoreFileSelect(
                config=self._config,
                config_key=setting_name,
                options=options,
                caption=options["ui_title"],
                directory=f"{CoreArgs._core_app_dir}",  # Starting directory
                filter=options["ui_file_filter"],
                initial_filter=options["ui_file_filter"],
                parent_key=self._parent_key,
                parent=parent,
            )
        elif card_type == UITypes.LINE_EDIT:
            widget = CoreLineEdit(
                config=self._config,
                config_key=setting_name,
                options=options,
                is_tight=self._is_tight,
                invalidmsg=(
                    options["ui_invalidmsg"] if "ui_invalidmsg" in options else ""
                ),
                tooltip=None,
                parent_key=self._parent_key,
                parent=parent,
            )
        elif card_type == UITypes.SLIDER:
            widget = CoreSlider(
                config=self._config,
                config_key=setting_name,
                options=options,
                num_range=[options["min"], options["max"]],
                is_tight=self._is_tight,
                baseunit=parseUnit(setting_name, options, self._config_name),
                parent_key=self._parent_key,
                parent=parent,
            )
        elif card_type == UITypes.SPINBOX:
            widget = CoreSpinBox(
                config=self._config,
                config_key=setting_name,
                options=options,
                min_value=options["min"],
                parent_key=self._parent_key,
                parent=parent,
            )
        elif card_type == UITypes.SWITCH:
            widget = CoreSwitch(
                config=self._config,
                config_key=setting_name,
                options=options,
                parent_key=self._parent_key,
                parent=parent,
            )
        else:
            err_msg = (
                f"Config '{self._config_name}': Invalid ui_type '{card_type}' for setting '{setting_name}'. "
                + f"Expected one of '{iterToString(UITypes._member_names_, separator=', ')}'"
            )
            raise TypeError(err_msg)
        return widget

    def _generateCards(self, CardGroup: AnyCardGroup) -> list[AnyCardGroup]:
        template = self._template.getTemplate()
        template_parser = TemplateParser()
        template_parser.parse(self._template_name, template)
        failed_cards = 0

        for section_name, section in template.items():
            card_group = CardGroup(
                f"{section_name}", self._parent
            )  # type: AnyCardGroup
            for setting, options in section.items():

                if "ui_flags" in options and UIFlags.EXCLUDE in options["ui_flags"]:
                    self._logger.debug(
                        f"Config '{self._config_name}': Excluding setting '{setting}' from GUI"
                    )
                    continue

                # Get the raw ui_group
                raw_group = f"{options["ui_group"]}" if "ui_group" in options else None

                # Split the ui_groups associated with this setting
                formatted_groups = (
                    template_parser.formatGroup(self._template_name, raw_group)
                    if raw_group
                    else None
                )

                # If multiple groups are defined for a setting, the first is considered the main group
                main_group = (
                    Group.getGroup(self._template_name, formatted_groups[0])
                    if formatted_groups
                    else None
                )
                all_groups = []
                if formatted_groups:
                    for format_group in formatted_groups:
                        group = Group.getGroup(self._template_name, format_group)
                        if group:
                            all_groups.append(group)
                if not all_groups:
                    all_groups = None

                try:
                    card = self._createCard(
                        card_type=inferType(setting, options, self._config_name),
                        setting=setting,
                        options=options,
                        content=options["ui_desc"] if "ui_desc" in options else "",
                        group=main_group,
                        parent=card_group,
                    )
                except Exception:
                    self._logger.error(
                        f"Config '{self._config_name}': Error creating setting card for setting '{setting}'\n"
                        + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
                    )
                    card = None
                if card:
                    if updateCardGrouping(
                        setting=setting,
                        card_group=card_group,
                        card=card,
                        groups=all_groups,
                    ):
                        self._updateCardSortOrder(card, card_group)
                else:
                    if main_group:
                        try:
                            # Remove the failed card from its group
                            main_group.removeChild(setting)
                        except KeyError:
                            # This card is a parent card
                            main_group.removeGroup(
                                self._template_name, main_group.getGroupName()
                            )
                    failed_cards += 1

            if self._hide_group_label:
                card_group.getTitleLabel().setHidden(True)

            if self._default_group:
                if self._default_group == card_group.getTitleLabel().text():
                    self._default_group = card_group
            else:
                self._default_group = card_group

            self._card_list.append(card_group)

        final_all_groups = Group.getAllGroups(self._template_name)

        if final_all_groups:
            UIGrouping.connectUIGroups(final_all_groups)
        self._addCardsBySortOrder()

        if failed_cards:
            setting_grammar = "setting" if failed_cards == 1 else "settings"
            core_signalbus.genericError.emit(
                f"Failed to create {failed_cards} {setting_grammar}",
                "See log for details",
            )

        return self._card_list

    def _updateCardSortOrder(
        self, card: AnySettingCard, cardGroup: AnyCardGroup
    ) -> None:
        card_group_name = f"{cardGroup}"
        if card_group_name not in self._card_sort_order:
            self._card_sort_order |= {card_group_name: []}
        self._card_sort_order.get(card_group_name).append(card)

    def _addCardsBySortOrder(self) -> None:
        for i, card_group in enumerate(self._getCardList()):
            cards = self._card_sort_order.get(f"{card_group}")
            if cards:
                for card in cards:
                    card_group.addSettingCard(card)
            else:
                self._logger.warning(
                    f"Config '{self._config_name}': Card group '{card_group.getTitleLabel().text()}' has no cards assigned to it. Removing"
                )
                card_group.deleteLater()
                self._getCardList().pop(i)

    def _getCardList(self) -> list[AnyCardGroup]:
        """Temp placement of unsorted cards"""
        return self._card_list

    def getCards(self) -> list[AnyCardGroup]:
        return self._cards

    def getDefaultGroup(self) -> AnyCardGroup:
        return self._default_group
