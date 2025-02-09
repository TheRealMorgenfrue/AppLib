import traceback
from abc import abstractmethod
from typing import Any, Optional

from PyQt6.QtWidgets import QWidget

from ...module.configuration.internal.core_args import CoreArgs
from ...module.configuration.tools.template_options.groups import Group
from ...module.configuration.tools.template_options.template_enums import (
    UIFlags,
    UITypes,
)
from ...module.configuration.tools.template_parser import TemplateParser
from ...module.exceptions import OrphanGroupWarning
from ...module.logging import AppLibLogger
from ...module.tools.types.config import AnyConfig
from ...module.tools.types.gui_cardgroups import AnyCardGroup
from ...module.tools.types.gui_cards import AnyCard, AnySettingCard
from ...module.tools.types.gui_settings import AnySetting
from ...module.tools.types.templates import AnyTemplate
from ...module.tools.utilities import iter_to_str
from ..common.core_signalbus import core_signalbus
from ..components.settings.checkbox import CoreCheckBox
from ..components.settings.color_picker import CoreColorPicker
from ..components.settings.combobox import CoreComboBox
from ..components.settings.file_selection import CoreFileSelect
from ..components.settings.line_edit import CoreLineEdit
from ..components.settings.slider import CoreSlider
from ..components.settings.spinbox import CoreSpinBox
from ..components.settings.switch import CoreSwitch
from .generator_tools import GeneratorUtils


class GeneratorBase:
    _logger = AppLibLogger().getLogger()

    def __init__(
        self,
        config: AnyConfig,
        template: AnyTemplate,
        default_group: Optional[str] = None,
        hide_group_label: bool = True,
        is_tight: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        if config.failure:
            err_msg = f"Config '{config.name}' is invalid"
            raise RuntimeError(err_msg)
        self._config = config
        self._template = template
        self._config_name = config.name
        self._default_group = default_group
        self._hide_group_label = hide_group_label
        self._is_tight = is_tight
        self._parent = parent

        # type: dict[str, list] # Mapping of the correct card sort order.
        self._card_sort_order = {}
        # type: list[AnyCardGroup] # Temp placement of unsorted cards.
        self._card_list = []
        # type: list[AnyCardGroup] # The cards sorted correctly.
        self._cards = []

    def _prefix_msg(self) -> str:
        return f"Config '{self._config_name}':"

    @abstractmethod
    def _createCard(
        self,
        card_type: UITypes,
        setting: str,
        options: dict[str, Any],
        parent_keys: list[str],
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

        parent_keys : list[str]
            The parents of `key`. Used for lookup in the config.

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
        key: str,
        options: dict,
        parent_keys: list[str],
        parent: Optional[QWidget] = None,
    ) -> AnySetting | None:
        """
        Create a setting widget for use on a setting card.

        Parameters
        ----------
        card_type : UITypes
            The type of the setting, e.g., Switch.

        key : str
            The setting's key in the config.

        options : dict
            The options available for this setting, e.g., its default value.

        parent_keys : list[str]
            The parents of `key`. Used for lookup in the config.

        parent : QWidget, optional
            The parent widget of this setting.
            By default `None`.

        Returns
        -------
        AnySetting | None
            The setting widget object if created succesfully, else `None`.
        """
        if card_type == UITypes.CHECKBOX:
            widget = CoreCheckBox(
                config=self._config,
                config_key=key,
                options=options,
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.COLOR_PICKER:
            widget = CoreColorPicker(
                config=self._config,
                config_key=key,
                options=options,
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.COMBOBOX:
            widget = CoreComboBox(
                config=self._config,
                config_key=key,
                options=options,
                texts=options["values"],
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.FILE_SELECTION:
            widget = CoreFileSelect(
                config=self._config,
                config_key=key,
                options=options,
                caption=options["ui_title"],
                directory=f"{CoreArgs._core_app_dir}",  # Starting directory
                filter=options["ui_file_filter"],
                initial_filter=options["ui_file_filter"],
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.LINE_EDIT:
            widget = CoreLineEdit(
                config=self._config,
                config_key=key,
                options=options,
                is_tight=self._is_tight,
                ui_invalidmsg=(
                    options["ui_invalidmsg"] if "ui_invalidmsg" in options else ""
                ),
                tooltip=None,
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.SLIDER:
            widget = CoreSlider(
                config=self._config,
                config_key=key,
                options=options,
                num_range=[options["min"], options["max"]],
                is_tight=self._is_tight,
                baseunit=GeneratorUtils.parseUnit(key, options, self._config_name),
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.SPINBOX:
            widget = CoreSpinBox(
                config=self._config,
                config_key=key,
                options=options,
                min_value=options["min"],
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.SWITCH:
            widget = CoreSwitch(
                config=self._config,
                config_key=key,
                options=options,
                parent_keys=parent_keys,
                parent=parent,
            )
        else:
            err_msg = (
                f"{self._prefix_msg()} Invalid ui_type '{card_type}' for setting '{key}'. "
                + f"Expected one of '{iter_to_str(UITypes._member_names_, separator=', ')}'"
            )
            raise TypeError(err_msg)
        return widget

    def _excludeSetting(self, setting: str, options: dict) -> bool:
        exclude = "ui_flags" in options and UIFlags.EXCLUDE in options["ui_flags"]
        if exclude:
            self._logger.debug(
                f"{self._prefix_msg()} Excluding setting '{setting}' from GUI"
            )
        return exclude

    def _generateCards(self, CardGroup: AnyCardGroup | None) -> list[AnyCardGroup]:
        template_parser = TemplateParser()
        template_parser.parse(self._template)
        failed_cards = 0

        card_groups = {}  # type: dict[str, AnyCardGroup]
        for k, v, pos, ps in self._template.get_settings():
            setting, options = next(iter(v.items()))

            if self._excludeSetting(setting, options):
                continue

            section_name = ps[-1]
            try:
                card_group = card_groups[section_name]
            except KeyError:
                card_group = (
                    CardGroup(section_name, self._parent) if CardGroup else None
                )
                card_groups[section_name] = card_group

            # Get the raw ui_group
            raw_group = f"{options["ui_group"]}" if "ui_group" in options else None
            try:
                # Split the ui_groups associated with this setting
                formatted_groups = (
                    template_parser.format_raw_group(self._template.name, raw_group)
                    if raw_group
                    else None
                )
            except OrphanGroupWarning:
                self._logger.warning(
                    f"{self._prefix_msg()} Cannot create card for orphan setting '{setting}'"
                )
                continue
            # If multiple groups are defined for a setting, the first is considered the main group
            main_group = (
                Group.getGroup(self._template.name, formatted_groups[0])
                if formatted_groups
                else None
            )

            try:
                card = self._createCard(
                    card_type=GeneratorUtils.inferType(
                        setting, options, self._config_name
                    ),
                    setting=setting,
                    options=options,
                    parent_keys=ps,
                    content=options["ui_desc"] if "ui_desc" in options else "",
                    group=main_group,
                    parent=card_group,
                )
            except Exception:
                self._logger.error(
                    f"{self._prefix_msg()} Error creating setting card for setting '{setting}'\n"
                    + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
                )
                card = None

            if card:
                all_groups = []
                if formatted_groups:
                    for format_group in formatted_groups:
                        group = Group.getGroup(self._template.name, format_group)
                        if group:
                            all_groups.append(group)
                if not all_groups:
                    all_groups = None
                if GeneratorUtils.updateCardGrouping(
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
                            self._template.name, main_group.getGroupName()
                        )
                failed_cards += 1

            if card_group:
                if self._hide_group_label:
                    card_group.getTitleLabel().setHidden(True)
                if isinstance(self._default_group, str):
                    if self._default_group == card_group.getTitleLabel().text():
                        self._default_group = card_group
                elif self._default_group is None:
                    self._default_group = card_group
            self._card_list.append(card_group)

        final_all_groups = Group.getAllGroups(self._template.name)
        if final_all_groups:
            GeneratorUtils.connectUIGroups(final_all_groups)
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
            self._card_sort_order[card_group_name] = []
        self._card_sort_order.get(card_group_name).append(card)

    def _addCardsBySortOrder(self) -> None:
        for card_group in list(self._getCardList()):
            cards = self._card_sort_order.get(f"{card_group}")
            if cards:
                for card in cards:
                    card_group.addSettingCard(card)
            else:
                self._logger.warning(
                    f"{self._prefix_msg()} Card group '{card_group.getTitleLabel().text()}' has no cards assigned to it. Removing"
                )
                card_group.deleteLater()
                self._getCardList().remove(card_group)

    def _getCardList(self) -> list[AnyCardGroup]:
        """Temp placement of unsorted cards"""
        return self._card_list

    def getCards(self) -> list[AnyCardGroup]:
        return self._cards

    def getDefaultGroup(self) -> AnyCardGroup:
        return self._default_group
