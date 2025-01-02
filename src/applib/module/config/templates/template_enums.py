from enum import Enum


class UIGroups(Enum):
    """Enums for ui_group_parent features"""

    # This setting and its children will be clustered together.
    # Essentially a 'flat' NESTED_CHILDREN, i.e. they're all nested on the same level.
    # CLUSTERED and NESTED_CHILDREN are mutually exclusive!
    CLUSTERED = 0  # (Applies to: All)

    # This setting's children will be nested under it.
    # However, the specifics of the nesting depend on the GUI Generator used.
    # NESTED_CHILDREN and CLUSTERED are mutually exclusive!
    NESTED_CHILDREN = 1  # (Applies to: All)

    # This setting disables all child settings in its group when it changes state.
    DISABLE_CHILDREN = 4  # (Applies to: All)

    # This setting's children will change their value according to their parent.
    SYNC_CHILDREN = 6  # (Applies to: Switch, CheckBox)

    # This setting's children will change their value opposite of their parent.
    DESYNC_CHILDREN = 7  # (Applies to: Switch, CheckBox)

    # This setting's children will change their value according to the value of the parent.
    # If Parent is True, then Child is True.
    # Example:
    #   Parent = True --> Child = True
    #   Parent = False --> Child = <current_value>
    DESYNC_TRUE_CHILDREN = 8  # (Applies to: Switch, CheckBox)

    # This setting's children will change their value according to the value of the parent.
    # If Parent is True, then Child is False
    # Example:
    #   Parent = True --> Child = False
    #   Parent = False --> Child = <current_value>
    DESYNC_FALSE_CHILDREN = 9  # (Applies to: Switch, CheckBox)


class UITypes(Enum):
    """Enums for specifying GUI widget types"""

    # True/False
    CHECKBOX = 0

    # Select color from color space
    COLOR_PICKER = 3

    # Drop-down select one of X possible values
    COMBOBOX = 6

    # Select file
    FILE_SELECTION = 9

    # One-line text field
    LINE_EDIT = 12

    # Sliding integer range
    SLIDER = 15

    # Integer/float input in an allowed range
    SPINBOX = 18

    # True/False
    SWITCH = 21


class UIFlags(Enum):
    """Special GUI flags that apply to individual settings"""

    # Setting requires a full reload of the app to take effect
    # The user is informed of this in the GUI
    REQUIRES_RELOAD = 0

    # Exclude this setting from the GUI.
    # No GUI element will be created for this setting.
    EXCLUDE = 1
