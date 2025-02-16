import traceback
from typing import Iterable

from ...module.configuration.internal.core_args import CoreArgs
from ...module.configuration.tools.template_options.groups import Group
from ...module.configuration.tools.template_options.options import GUIOption
from ...module.configuration.tools.template_options.template_enums import (
    UIGroups,
    UITypes,
)
from ...module.logging import AppLibLogger
from ...module.tools.types.gui_cardgroups import AnyCardGroup
from ...module.tools.types.gui_cards import AnyCard, AnyParentCard
from ...module.tools.types.gui_settings import AnyBoolSetting
from ...module.tools.utilities import iter_to_str
from ..components.settingcards.card_base import DisableWrapper


class GeneratorUtils:
    _logger = AppLibLogger().get_logger()

    @classmethod
    def _ensure_bool_child(cls, parent: AnyParentCard, child: AnyCard, group: Group):
        """Used for all sync/desync Groups"""
        parent_option = parent.get_option()
        child_option = child.get_option()

        if isinstance(parent_option, AnyBoolSetting) and isinstance(
            child_option, AnyBoolSetting
        ):
            return True
        else:
            cls._logger.warning(
                f"UI Group '{group.get_group_name()}': "
                + f"The option of both parent and child must be a strictly boolean setting (e.g. switch). "
                + f"Parent '{parent.get_card_name()}' has option of type '{type(parent_option).__name__}', "
                + f"child '{child.get_card_name()}' has option of type '{type(child_option).__name__}'"
            )
            return False

    @classmethod
    def _sync_children(cls, wrapper: DisableWrapper | bool, child: AnyCard) -> None:
        # Result == Input
        if isinstance(wrapper, DisableWrapper):
            child.get_disablesignal().emit(wrapper)
        else:
            child.get_option().set_config_value(wrapper)

    @classmethod
    def _desync_children(cls, wrapper: DisableWrapper | bool, child: AnyCard) -> None:
        # Result == !Input
        if isinstance(wrapper, DisableWrapper):
            wrapper.is_disabled = not wrapper.is_disabled
            child.get_disablesignal().emit(wrapper)
        else:
            child.get_option().set_config_value(not wrapper)

    @classmethod
    def _desync_true_children(
        cls, wrapper: DisableWrapper | bool, child: AnyCard
    ) -> None:
        # Input ? Result == Input : pass
        if isinstance(wrapper, DisableWrapper) and wrapper.is_disabled or wrapper:
            cls._sync_children(wrapper, child)

    @classmethod
    def _desync_false_children(
        cls, wrapper: DisableWrapper | bool, child: AnyCard
    ) -> None:
        # Input ? Result == !Input : pass
        if isinstance(wrapper, DisableWrapper) and wrapper.is_disabled or wrapper:
            cls._desync_children(wrapper, child)

    @classmethod
    def connect_ui_groups(cls, ui_groups: Iterable[Group]):
        for group in ui_groups:
            ui_group_parent = group.get_ui_group_parent()
            parent = group.get_parent_card()
            is_disabled = False
            try:
                parent_option = parent.get_option()
            except AttributeError:
                cls._logger.error(
                    f"Template '{group.get_template_name()}': Unable to connect cards in UI group '{group.get_group_name()}' "
                    + f"due to missing card for parent setting '{group.get_parent_name()}'"
                )
                continue
            try:
                if (
                    UIGroups.NESTED_CHILDREN in ui_group_parent
                    or UIGroups.CLUSTERED in ui_group_parent
                ):
                    group.enforce_logical_nesting()
                    for child in group.get_child_cards():
                        parent.add_child(child)

                if UIGroups.DISABLE_CHILDREN in ui_group_parent:
                    for child in group.get_child_cards():
                        if UIGroups.SYNC_CHILDREN in ui_group_parent:
                            is_disabled = True
                            parent.get_disable_children_signal().connect(
                                lambda wrapper, child=child: cls._sync_children(
                                    wrapper, child
                                )
                            )

                        if UIGroups.DESYNC_CHILDREN in ui_group_parent:
                            is_disabled = True
                            parent.get_disable_children_signal().connect(
                                lambda wrapper, child=child: cls._desync_children(
                                    wrapper, child
                                )
                            )

                        if UIGroups.DESYNC_TRUE_CHILDREN in ui_group_parent:
                            is_disabled = True
                            parent.get_disable_children_signal().connect(
                                lambda wrapper, child=child: cls._desync_true_children(
                                    wrapper, child
                                )
                            )

                        if UIGroups.DESYNC_FALSE_CHILDREN in ui_group_parent:
                            is_disabled = True
                            parent.get_disable_children_signal().connect(
                                lambda wrapper, child=child: cls._desync_false_children(
                                    wrapper, child
                                )
                            )

                        if not is_disabled:
                            parent.get_disable_children_signal().connect(
                                child.get_disablesignal().emit
                            )

                if not is_disabled:
                    if UIGroups.SYNC_CHILDREN in ui_group_parent:
                        for child in group.get_child_cards():
                            if cls._ensure_bool_child(parent, child, group):
                                parent_option.getCheckedSignal().connect(
                                    lambda checked, child=child: cls._sync_children(
                                        checked, child
                                    )
                                )

                    if UIGroups.DESYNC_CHILDREN in ui_group_parent:
                        for child in group.get_child_cards():
                            if cls._ensure_bool_child(parent, child, group):
                                parent_option.getCheckedSignal().connect(
                                    lambda checked, child=child: cls._desync_children(
                                        checked, child
                                    )
                                )

                    if UIGroups.DESYNC_TRUE_CHILDREN in ui_group_parent:
                        for child in group.get_child_cards():
                            if cls._ensure_bool_child(parent, child, group):
                                parent_option.getCheckedSignal().connect(
                                    lambda checked, child=child: cls._desync_true_children(
                                        checked, child
                                    )
                                )

                    if UIGroups.DESYNC_FALSE_CHILDREN in ui_group_parent:
                        for child in group.get_child_cards():
                            if cls._ensure_bool_child(parent, child, group):
                                parent_option.getCheckedSignal().connect(
                                    lambda checked, child=child: cls._desync_false_children(
                                        checked, child
                                    )
                                )

                # Update parent's and its children's disable status
                if not group.is_nested_child():
                    parent.notifyCard.emit(("updateState", None))
            except Exception:
                cls._logger.error(
                    f"Template '{group.get_template_name()}': An unknown error occurred while connecting cards in UI group '{group.get_group_name()}'\n"
                    + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
                )

    @classmethod
    def update_card_grouping(
        cls,
        setting: str,
        card: AnyCard,
        card_group: AnyCardGroup | None,
        groups: Iterable[Group] | None,
    ) -> bool:
        not_nested = True
        if groups:
            for group in groups:
                if setting == group.get_parent_name():
                    # Note: parents are not added to the setting card group here,
                    # since a parent can be a child of another parent
                    group.set_parent_card(card)
                    group.set_parent_card_group(
                        card_group
                    )  # Instead, save a reference to the card group
                else:
                    uiGroups = group.get_ui_group_parent()
                    if (
                        UIGroups.NESTED_CHILDREN in uiGroups
                        or UIGroups.CLUSTERED in uiGroups
                    ):
                        not_nested = False  # Any nested setting must not be added directly to the card group
                    group.add_child_card(card)
                    group.add_child_card_group(setting, card_group)
        return not_nested

    @classmethod
    def infer_type(
        cls, setting: str, option: GUIOption, config_name: str
    ) -> UITypes | None:
        """Infer card type from various options in the template"""
        card_type = None
        if option.defined(option.ui_type):
            card_type = option.ui_type
        elif option.defined(option.ui_invalid_input):
            # TODO: ui_invalid_input should apply to all free-form input
            card_type = UITypes.LINE_EDIT
        elif (
            option.defined(option.max)
            and option.max is None
            or not option.defined(option.max)
            and option.defined(option.min)
        ):
            card_type = UITypes.SPINBOX
        elif isinstance(option.default, bool):
            card_type = UITypes.SWITCH
        elif isinstance(option.default, int):
            card_type = UITypes.SLIDER
        elif isinstance(option.default, str):
            card_type = UITypes.LINE_EDIT  # FIXME: Temporary
        else:
            cls._logger.warning(
                f"Config '{config_name}': Failed to infer ui_type for setting '{setting}'. "
                + f"The default value '{option.default}' has unsupported type '{type(option.default).__name__}'"
            )
        return card_type

    @classmethod
    def parse_unit(
        cls, setting: str, option: GUIOption, config_name: str
    ) -> str | None:
        baseunit = None
        if option.defined(option.ui_unit):
            baseunit = option.ui_unit
            if baseunit not in CoreArgs._core_config_units.keys():
                cls._logger.warning(
                    f"Config '{config_name}': Setting '{setting}' has invalid unit '{baseunit}'. "
                    + f"Expected one of '{iter_to_str(CoreArgs._core_config_units.keys(), separator=', ')}'"
                )
        return baseunit
