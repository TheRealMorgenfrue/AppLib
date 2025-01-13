import traceback
from typing import Iterable

from ..components.settingcards.card_base import DisableWrapper
from ...module.config.internal.core_args import CoreArgs
from ...module.config.templates.template_enums import UIGroups, UITypes
from ...module.config.tools.template_options.groups import Group
from ...module.logging import AppLibLogger
from ...module.tools.types.gui_cardgroups import AnyCardGroup
from ...module.tools.types.gui_cards import AnyCard, AnyParentCard
from ...module.tools.types.gui_settings import AnyBoolSetting
from ...module.tools.utilities import iterToString


_logger_ = AppLibLogger().getLogger()


class UIGrouping:

    @classmethod
    def _ensure_bool_child(cls, parent: AnyParentCard, child: AnyCard, group: Group):
        """Used for all sync/desync Groups"""
        parent_option = parent.getOption()
        child_option = child.getOption()

        if isinstance(parent_option, AnyBoolSetting) and isinstance(
            child_option, AnyBoolSetting
        ):
            return True
        else:
            _logger_.warning(
                f"UI Group '{group.getGroupName()}': "
                + f"The option of both parent and child must be a strictly boolean setting (e.g. switch). "
                + f"Parent '{parent.getCardName()}' has option of type '{type(parent_option).__name__}', "
                + f"child '{child.getCardName()}' has option of type '{type(child_option).__name__}'"
            )
            return False

    @classmethod
    def _sync_children(cls, wrapper: DisableWrapper | bool, child: AnyCard) -> None:
        # Result == Input
        if isinstance(wrapper, DisableWrapper):
            child.getDisableSignal().emit(wrapper)
        else:
            child.getOption().setConfigValue(wrapper)

    @classmethod
    def _desync_children(cls, wrapper: DisableWrapper | bool, child: AnyCard) -> None:
        # Result == !Input
        if isinstance(wrapper, DisableWrapper):
            wrapper.is_disabled = not wrapper.is_disabled
            child.getDisableSignal().emit(wrapper)
        else:
            child.getOption().setConfigValue(not wrapper)

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
    def connectUIGroups(cls, ui_groups: Iterable[Group]):
        for group in ui_groups:
            uiGroupParent = group.getUIGroupParent()
            parent = group.getParentCard()
            is_disabled = False
            try:
                parent_option = parent.getOption()
            except AttributeError:
                _logger_.warning(
                    f"Template '{group.getTemplateName()}': Unable to connect cards in UI group '{group.getGroupName()}' due to missing card for parent setting '{group.getParentName()}'. Skipping UI group"
                )
                continue
            try:
                if (
                    UIGroups.NESTED_CHILDREN in uiGroupParent
                    or UIGroups.CLUSTERED in uiGroupParent
                ):
                    group.enforceLogicalNesting()
                    for child in group.getChildCards():
                        parent.addChild(child)

                if UIGroups.DISABLE_CHILDREN in uiGroupParent:
                    for child in group.getChildCards():
                        if UIGroups.SYNC_CHILDREN in uiGroupParent:
                            is_disabled = True
                            parent.getDisableChildrenSignal().connect(
                                lambda wrapper, child=child: cls._sync_children(
                                    wrapper, child
                                )
                            )

                        if UIGroups.DESYNC_CHILDREN in uiGroupParent:
                            is_disabled = True
                            parent.getDisableChildrenSignal().connect(
                                lambda wrapper, child=child: cls._desync_children(
                                    wrapper, child
                                )
                            )

                        if UIGroups.DESYNC_TRUE_CHILDREN in uiGroupParent:
                            is_disabled = True
                            parent.getDisableChildrenSignal().connect(
                                lambda wrapper, child=child: cls._desync_true_children(
                                    wrapper, child
                                )
                            )

                        if UIGroups.DESYNC_FALSE_CHILDREN in uiGroupParent:
                            is_disabled = True
                            parent.getDisableChildrenSignal().connect(
                                lambda wrapper, child=child: cls._desync_false_children(
                                    wrapper, child
                                )
                            )

                        if not is_disabled:
                            parent.getDisableChildrenSignal().connect(
                                child.getDisableSignal().emit
                            )

                if not is_disabled:
                    if UIGroups.SYNC_CHILDREN in uiGroupParent:
                        for child in group.getChildCards():
                            if cls._ensure_bool_child(parent, child, group):
                                parent_option.getCheckedSignal().connect(
                                    lambda checked, child=child: cls._sync_children(
                                        checked, child
                                    )
                                )

                    if UIGroups.DESYNC_CHILDREN in uiGroupParent:
                        for child in group.getChildCards():
                            if cls._ensure_bool_child(parent, child, group):
                                parent_option.getCheckedSignal().connect(
                                    lambda checked, child=child: cls._desync_children(
                                        checked, child
                                    )
                                )

                    if UIGroups.DESYNC_TRUE_CHILDREN in uiGroupParent:
                        for child in group.getChildCards():
                            if cls._ensure_bool_child(parent, child, group):
                                parent_option.getCheckedSignal().connect(
                                    lambda checked, child=child: cls._desync_true_children(
                                        checked, child
                                    )
                                )

                    if UIGroups.DESYNC_FALSE_CHILDREN in uiGroupParent:
                        for child in group.getChildCards():
                            if cls._ensure_bool_child(parent, child, group):
                                parent_option.getCheckedSignal().connect(
                                    lambda checked, child=child: cls._desync_false_children(
                                        checked, child
                                    )
                                )

                # Update parent's and its children's disable status
                if not group.isNestedChild():
                    parent.notifyCard.emit(("updateState", None))
            except Exception:
                _logger_.error(
                    f"Template '{group.getTemplateName()}': An unknown error occurred while connecting cards in UI group '{group.getGroupName()}'\n"
                    + traceback.format_exc(limit=CoreArgs._core_traceback_limit)
                )
                continue


def updateCardGrouping(
    setting: str,
    card_group: AnyCardGroup,
    card: AnyCard,
    groups: Iterable[Group] | None,
) -> bool:
    not_nested = True
    if groups:
        for group in groups:
            if setting == group.getParentName():
                # Note: parents are not added to the setting card group here,
                # since a parent can be a child of another parent
                group.setParentCard(card)
                group.setParentCardGroup(
                    card_group
                )  # Instead, save a reference to the card group
            else:
                uiGroups = group.getUIGroupParent()
                if (
                    UIGroups.NESTED_CHILDREN in uiGroups
                    or UIGroups.CLUSTERED in uiGroups
                ):
                    not_nested = False  # Any nested setting must not be added directly to the card group
                group.addChildCard(card)
                group.addChildCardGroup(setting, card_group)
    return not_nested


def inferType(setting: str, options: dict, config_name: str) -> UITypes | None:
    """Infer card type from various options in the template"""
    card_type = None
    if "ui_type" in options:
        card_type = options["ui_type"]
    elif "ui_invalidmsg" in options:
        card_type = (
            UITypes.LINE_EDIT
        )  # TODO: ui_invalidmsg should apply to all free-form input
    elif (
        "max" in options
        and options["max"] is None
        or "max" not in options
        and "min" in options
    ):
        card_type = UITypes.SPINBOX
    elif isinstance(options["default"], bool):
        card_type = UITypes.SWITCH
    elif isinstance(options["default"], int):
        card_type = UITypes.SLIDER
    elif isinstance(options["default"], str):
        card_type = UITypes.LINE_EDIT  # FIXME: Temporary
    else:
        _logger_.warning(
            f"Config '{config_name}': Failed to infer ui_type for setting '{setting}'. "
            + f"The default value '{options["default"]}' has unsupported type '{type(options["default"])}'"
        )
    return card_type


def parseUnit(setting: str, options: dict, config_name: str) -> str | None:
    baseunit = None
    if "ui_unit" in options:
        baseunit = options["ui_unit"]
        if baseunit not in CoreArgs._core_config_units.keys():
            _logger_.warning(
                f"Config '{config_name}': Setting '{setting}' has invalid unit '{baseunit}'. "
                + f"Expected one of '{iterToString(CoreArgs._core_config_units.keys(), separator=', ')}'"
            )
    return baseunit
