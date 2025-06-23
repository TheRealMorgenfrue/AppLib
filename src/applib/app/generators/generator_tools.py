import traceback
from collections.abc import Callable, Iterable

from PyQt6.QtCore import pyqtBoundSignal

from ...app.common.auto_wrap import AutoTextWrap
from ...module.configuration.internal.core_args import CoreArgs
from ...module.configuration.tools.template_utils.groups import Group
from ...module.configuration.tools.template_utils.options import GUIOption
from ...module.configuration.tools.template_utils.template_enums import (
    UIGroups,
    UITypes,
)
from ...module.logging import LoggingManager
from ...module.tools.types.gui_cardgroups import AnyCardGroup
from ...module.tools.types.gui_cards import AnyCard, AnyParentCard
from ...module.tools.types.gui_settings import AnyBoolSetting
from ...module.tools.utilities import iter_to_str
from ..components.settingcards.card_base import DisableWrapper


class GeneratorUtils:
    @classmethod
    def _check_bool(cls, parent: AnyParentCard, child: AnyCard):
        """Used for all sync/desync Groups"""
        parent_option = parent.get_option()
        child_option = child.get_option()

        if isinstance(parent_option, AnyBoolSetting) and isinstance(
            child_option, AnyBoolSetting
        ):
            return True
        else:
            return False

    @classmethod
    def _update_signal_slots(
        cls,
        ss: dict[pyqtBoundSignal, list[Callable]],
        signal: pyqtBoundSignal,
        slots: list[Callable],
    ):
        try:
            if signal is not None:
                ss[signal].extend(slots)
        except KeyError:
            ss[signal] = [*slots]

    @classmethod
    def _sync_children(cls, wrapper: DisableWrapper | bool, child: AnyCard) -> None:
        # Result == Input
        if isinstance(wrapper, DisableWrapper):
            child.getDisableSignal().emit(wrapper)
        else:
            child.get_option().setConfigValue(wrapper)

    @classmethod
    def _desync_children(cls, wrapper: DisableWrapper | bool, child: AnyCard) -> None:
        # Result == !Input
        if isinstance(wrapper, DisableWrapper):
            wrapper.is_disabled = not wrapper.is_disabled
            child.getDisableSignal().emit(wrapper)
        else:
            child.get_option().setConfigValue(not wrapper)

    @classmethod
    def _desync_true_children(
        cls, wrapper: DisableWrapper | bool, child: AnyCard
    ) -> None:
        # Result == Input ? Input : pass
        if isinstance(wrapper, DisableWrapper) and wrapper.is_disabled or wrapper:
            cls._sync_children(wrapper, child)

    @classmethod
    def _desync_false_children(
        cls, wrapper: DisableWrapper | bool, child: AnyCard
    ) -> None:
        # Result == !Input ? Input : pass
        if isinstance(wrapper, DisableWrapper) and wrapper.is_disabled or wrapper:
            cls._desync_children(wrapper, child)

    @classmethod
    def connect_ui_groups(cls, ui_groups: Iterable[Group]):
        logger = LoggingManager()
        for group in ui_groups:
            ui_group_parent = group.get_ui_group_parent()
            parent = group.get_parent_card()
            try:
                parent_option = parent.get_option()
            except AttributeError:
                logger.error(
                    AutoTextWrap.text_format(
                        f"""
                        Template '{group.get_template_name()}':
                        Unable to connect cards in UI group '{group.get_group_name()}'
                        due to missing card for parent setting '{group.get_parent_name()}'
                        """
                    ),
                    gui=True,
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

                disable_children = UIGroups.DISABLE_CHILDREN in ui_group_parent
                sync_children = UIGroups.SYNC_CHILDREN in ui_group_parent
                desync_children = UIGroups.DESYNC_CHILDREN in ui_group_parent
                desync_true_children = UIGroups.DESYNC_TRUE_CHILDREN in ui_group_parent
                desync_false_children = (
                    UIGroups.DESYNC_FALSE_CHILDREN in ui_group_parent
                )
                is_undirected = UIGroups.UNDIRECTED_SYNC in ui_group_parent
                signal_slots = {}  # type: dict[pyqtBoundSignal, list[Callable]]
                child_slots = []
                parent_slots = []
                for child in group.get_child_cards():
                    is_bool_child = cls._check_bool(parent, child)
                    func = None
                    if sync_children:
                        func = cls._sync_children
                    elif desync_children:
                        func = cls._desync_children
                    elif desync_true_children:
                        func = cls._desync_true_children
                    elif desync_false_children:
                        func = cls._desync_false_children
                    if func is not None:
                        if is_undirected:
                            parent_slots.append(
                                lambda wrapper_or_checked, parent=parent, func=func: func(
                                    wrapper_or_checked, parent
                                )
                            )
                        child_slots.append(
                            lambda wrapper_or_checked, child=child, func=func: func(
                                wrapper_or_checked, child
                            )
                        )
                    if disable_children:
                        if func is None:
                            child_slots.append(child.getDisableSignal().emit)

                        if is_undirected:
                            cls._update_signal_slots(
                                signal_slots, child.getDisableSignal(), parent_slots
                            )
                        cls._update_signal_slots(
                            signal_slots, parent.getDisableChildrenSignal(), child_slots
                        )
                    else:
                        if is_bool_child:
                            if is_undirected:
                                cls._update_signal_slots(
                                    signal_slots,
                                    child.get_option().getCheckedSignal(),
                                    parent_slots,
                                )
                            cls._update_signal_slots(
                                signal_slots,
                                parent_option.getCheckedSignal(),
                                child_slots,
                            )

                # Connect signals to slots
                for signal, child_slots in signal_slots.items():
                    for slot in child_slots:
                        signal.connect(slot)

                # Update parent's and its children's disable status
                if not group.is_nested_child():
                    parent.notifyCard.emit(("updateState", None))
            except Exception:
                LoggingManager().error(
                    AutoTextWrap.text_format(
                        f"""
                        Template '{group.get_template_name()}':
                        An error occurred while connecting cards in UI group '{group.get_group_name()}'/n
                        """
                    )
                    + traceback.format_exc(limit=CoreArgs._core_traceback_limit),
                    gui=True,
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
            LoggingManager().warning(
                AutoTextWrap.text_format(
                    f"""
                    Config '{config_name}': Failed to infer ui_type for setting '{setting}'.
                    The default value '{option.default}' has unsupported type '{type(option.default).__name__}'
                    """
                ),
                gui=True,
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
                LoggingManager().warning(
                    AutoTextWrap.text_format(
                        f"""
                        Config '{config_name}': Setting '{setting}' has invalid unit '{baseunit}'.
                        Expected one of [{iter_to_str(CoreArgs._core_config_units.keys(), separator=', ')}]
                        """
                    ),
                    gui=True,
                )
        return baseunit
