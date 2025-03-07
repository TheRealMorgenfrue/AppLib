from enum import Enum


class UIGroups(Enum):
    """Enums for template system's ui_group_parent features"""

    CLUSTERED = 0
    """
    This setting and its children will be clustered together.

    Essentially a 'flat' NESTED_CHILDREN, i.e. they're all nested on the same level.

    NOTE: CLUSTERED and NESTED_CHILDREN are mutually exclusive!
    #### Applies to: All
    """

    NESTED_CHILDREN = 1
    """
    This setting's children will be nested under it.

    However, the specifics of the nesting depend on the GUI Generator used.

    NOTE: NESTED_CHILDREN and CLUSTERED are mutually exclusive!
    #### Applies to: All
    """

    DISABLE_CHILDREN = 4
    """
    This setting disables all child settings in its group when it changes state.

    #### Applies to: All
    """

    UNDIRECTED_SYNC = 5
    """
    All synchronization directives (sync/desync) affects both ways, i.e. to parent and child.
    Without this, they affect only the children.

    #### Applies to: Booleans (e.g. Switch, CheckBox)
    """

    SYNC_CHILDREN = 6
    """
    This setting's children will change their value according to their parent.

    ##### Applies to: Booleans (e.g. Switch, CheckBox)
    """

    DESYNC_CHILDREN = 7
    """
    This setting's children will change their value opposite of their parent.

    #### Applies to: Booleans (e.g. Switch, CheckBox)
    """

    DESYNC_TRUE_CHILDREN = 8
    """
    This setting's children will change their value according to the value of the parent.

    If Parent is True, then Child is True.

    Example:
    ```
    if parent:
        child = True
    else:
        child = child
    ```

    #### Applies to: Booleans (e.g. Switch, CheckBox)
    """

    DESYNC_FALSE_CHILDREN = 9
    """
    This setting's children will change their value according to the value of the parent.

    If Parent is True, then Child is False

    Example:
    ```
    if parent:
        child = False
    else:
        child = child
    ```

    #### Applies to: Booleans (e.g. Switch, CheckBox)
    """


class UITypes(Enum):
    """Enums for specifying GUI widget types"""

    CHECKBOX = 0
    """
    Select a boolean value (True/False).
    """

    COLOR_PICKER = 3
    """
    Select color from RGB color space.
    """

    COMBOBOX = 6
    """
    Drop-down select one of X possible values.
    """

    FILE_SELECTION = 9
    """
    Select a file or folder on the file system.

    NOTE: Selection of multiple files not yet supported.
    """

    LINE_EDIT = 12
    """
    One-line editable text field.
    """

    SLIDER = 15
    """
    Sliding integer range.
    """

    SPINBOX = 18
    """
    Integer/float input in an allowed range.
    """

    SWITCH = 21
    """
    Select a boolean value (True/False).
    """


class UIFlags(Enum):
    """Special GUI flags that apply to individual settings"""

    REQUIRES_RELOAD = 0
    """
    Setting requires a full reload of the app to take effect.

    The user is informed of this in the GUI.
    """

    EXCLUDE = 1
    """
    Exclude this setting from the GUI.

    No GUI element will be created for this setting.
    """
