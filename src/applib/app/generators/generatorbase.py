import traceback
from abc import abstractmethod
from typing import Optional

from PyQt6.QtWidgets import QWidget

from ...module.configuration.internal.core_args import CoreArgs
from ...module.configuration.tools.template_parser import TemplateParser
from ...module.configuration.tools.template_utils.groups import Group
from ...module.configuration.tools.template_utils.options import GUIOption
from ...module.configuration.tools.template_utils.template_enums import UIFlags, UITypes
from ...module.exceptions import OrphanGroupWarning
from ...module.logging import LoggingManager
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

        self._logger = LoggingManager().applib_logger()
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
    def _create_card(
        self,
        card_type: UITypes,
        setting: str,
        option: GUIOption,
        parent_keys: list[str],
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

        option : GUIOption
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
            By default None.

        Returns
        -------
        AnyCard | None
            A setting card which can be displayed in a GUI.
        """
        ...

    def _create_setting(
        self,
        card_type: UITypes,
        key: str,
        option: GUIOption,
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

        option : GUIOption
            The options available for this setting, e.g., its default value.

        parent_keys : list[str]
            The parents of `key`. Used for lookup in the config.

        parent : QWidget, optional
            The parent widget of this setting.
            By default None.

        Returns
        -------
        AnySetting | None
            The setting widget object if created succesfully, else None.
        """
        converter = option.converter if option.defined(option.converter) else None
        if card_type == UITypes.CHECKBOX:
            widget = CoreCheckBox(
                config=self._config,
                config_key=key,
                option=option,
                converter=converter,
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.COLOR_PICKER:
            widget = CoreColorPicker(
                config=self._config,
                config_key=key,
                option=option,
                converter=converter,
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.COMBOBOX:
            widget = CoreComboBox(
                config=self._config,
                config_key=key,
                option=option,
                texts=option.values,
                converter=converter,
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.FILE_SELECTION:
            widget = CoreFileSelect(
                config=self._config,
                config_key=key,
                option=option,
                caption=option.ui_info.title,
                directory=f"{CoreArgs._core_app_dir}",  # Starting directory
                show_dir_only=option.ui_show_dir_only,
                filter=option.ui_file_filter,
                selected_filter=option.ui_file_filter,
                converter=converter,
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.LINE_EDIT:
            widget = CoreLineEdit(
                config=self._config,
                config_key=key,
                option=option,
                is_tight=self._is_tight,
                ui_invalid_input=option.ui_invalid_input,
                converter=converter,
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.SLIDER:
            widget = CoreSlider(
                config=self._config,
                config_key=key,
                option=option,
                num_range=(option.min, option.max),
                is_tight=self._is_tight,
                baseunit=GeneratorUtils.parse_unit(key, option, self._config_name),
                converter=converter,
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.SPINBOX:
            widget = CoreSpinBox(
                config=self._config,
                config_key=key,
                option=option,
                num_range=(option.min, option.max),
                converter=converter,
                parent_keys=parent_keys,
                parent=parent,
            )
        elif card_type == UITypes.SWITCH:
            widget = CoreSwitch(
                config=self._config,
                config_key=key,
                option=option,
                converter=converter,
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

    def _exclude_setting(self, setting: str, option: GUIOption) -> bool:
        exclude = option.defined(option.ui_flags) and UIFlags.EXCLUDE in option.ui_flags
        if exclude:
            self._logger.debug(
                f"{self._prefix_msg()} Excluding setting '{setting}' from GUI"
            )
        return exclude

    def _generate_cards(self, CardGroup: AnyCardGroup | None) -> list[AnyCardGroup]:
        template_parser = TemplateParser()
        template_parser.parse(self._template)
        card_groups = {}  # type: dict[str, AnyCardGroup]
        failed_cards = 0

        for k, v, pos, ps in self._template.get_settings():
            item = next(iter(v.items()))  # type: tuple[str, GUIOption]
            setting, option = item

            if self._exclude_setting(setting, option):
                continue

            # Create a card group a tie it to a section name if it does not exist already
            try:
                section_name = ps[-1]
                card_group = card_groups[section_name]
            except KeyError:
                card_group = (
                    CardGroup(section_name, self._parent) if CardGroup else None
                )
                card_groups[section_name] = card_group
            except IndexError:
                card_group = (
                    None  # Cannot create card group for a setting without section name
                )

            try:
                # Split the ui_groups associated with this setting
                formatted_groups = (
                    template_parser.format_raw_group(
                        self._template.name, option.ui_group
                    )
                    if option.defined(option.ui_group)
                    else None
                )
            except OrphanGroupWarning:
                self._logger.warning(
                    f"{self._prefix_msg()} Cannot create card for orphan setting '{setting}'"
                )
                continue
            except Exception:
                formatted_groups = None

            # If multiple groups are defined for a setting, the first is considered the main group
            main_group = (
                Group.get_group(self._template.name, formatted_groups[0])
                if formatted_groups
                else None
            )
            try:
                card = self._create_card(
                    card_type=GeneratorUtils.infer_type(
                        setting, option, self._config_name
                    ),
                    setting=setting,
                    option=option,
                    parent_keys=ps,
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
                        group = Group.get_group(self._template.name, format_group)
                        if group:
                            all_groups.append(group)
                if not all_groups:
                    all_groups = None
                if GeneratorUtils.update_card_grouping(
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
                        main_group.remove_child(setting)
                    except KeyError:
                        # This card is a parent card
                        main_group.remove_group(
                            self._template.name, main_group.get_group_name()
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
            elif card:
                self._card_list.append(card)

        final_all_groups = Group.get_all_groups(self._template.name)
        if final_all_groups:
            GeneratorUtils.connect_ui_groups(final_all_groups)
        self._addCardsBySortOrder()

        if failed_cards:
            setting_grammar = "setting" if failed_cards == 1 else "settings"
            core_signalbus.genericError.emit(
                f"Failed to create {failed_cards} {setting_grammar}",
                "See log for details",
            )
        return self._card_list

    def _updateCardSortOrder(
        self, card: AnySettingCard, cardGroup: AnyCardGroup | None
    ) -> None:
        if cardGroup is None:
            return
        card_group_name = f"{cardGroup}"
        if card_group_name not in self._card_sort_order:
            self._card_sort_order[card_group_name] = []
        self._card_sort_order.get(card_group_name).append(card)

    def _addCardsBySortOrder(self) -> None:
        for card_or_group in list(self._getCardList()):
            if isinstance(card_or_group, AnyCardGroup):
                cards = self._card_sort_order.get(f"{card_or_group}")
                if cards:
                    for card in cards:
                        card_or_group.addSettingCard(card)
                else:
                    self._logger.warning(
                        f"{self._prefix_msg()} Card group '{card_or_group.getTitleLabel().text()}' has no cards assigned to it. Removing"
                    )
                    card_or_group.deleteLater()
                    self._getCardList().remove(card_or_group)

    def _getCardList(self) -> list[AnyCardGroup]:
        """Temp placement of unsorted cards"""
        return self._card_list

    def getCards(self) -> list[AnyCardGroup]:
        return self._cards

    def getDefaultGroup(self) -> AnyCardGroup | None:
        return self._default_group
