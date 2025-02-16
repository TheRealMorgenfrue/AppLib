from numbers import Number
from typing import Any, Callable, Hashable, Union

from .template_enums import UIFlags, UIGroups, UITypes


class Undefined:
    """Denotes an argument as undefined. Is used to allow None as an Option argument"""

    pass


class GUIMessage:
    def __init__(self, title: str, description: str = ""):
        """
        A message informing the user of something.

        Parameters
        ----------
        title : str
            The title of the message.
        description : str, optional
            The description (or content) of the message.
            By default "".
        """
        self.title = title
        self.description = description


class Option:
    def __init__(
        self,
        default,
        actions: Callable | list[Callable] = Undefined,
        max: int = Undefined,
        min: int = Undefined,
        type: type = Undefined,
        validators: Callable | list[Callable] = Undefined,
    ):
        """Create an option instance usable in a non-GUI environment.

        An Option is the value of a setting, as defined in the template specification.

        Parameters
        ----------
        default : Any
            The default value for this setting.
        actions : Callable | list[Callable], optional
            Functions to call when this setting changes value.
            Each function must take one argument, which is the new value of this setting.
        max : int, optional
            The maximum value for this setting.
            If None, there is no limit.
        min : int, optional
            The minimum value for this setting.
            If None, there is no limit.
        type : type, optional
            The Python type for the value of this setting. For instance, 3 has type 'int'.
            NOTE: Types are also inferred from other arguments.
        validators : Callable | list[Callable], optional
            Functions used to validate the value of this setting (in addition to default Pydantic validation).
            Each function must take one argument, which is the value of this setting.
            If the value is invalid, they must raise either ValueError or AssertionError.
        """
        self.default = default
        self.actions = actions
        self.max = max
        self.min = min
        self.type = type
        self.validators = validators

    def __getattr__(self, name):
        """
        Called when the default attribute access fails with an AttributeError (either __getattribute__()
        raises an AttributeError because `name` is not an instance attribute or an attribute in the class tree
        for self; or __get__() of a `name` property raises AttributeError)
        """
        return Undefined

    def defined(self, attr_value) -> bool:
        """Whether the given attribute is defined. Returns True if it is."""
        return type(attr_value) != type(Undefined)


class GUIOption(Option):
    def __init__(
        self,
        default,
        actions: Callable | list[Callable] = Undefined,
        max: Number = Undefined,
        min: Number = Undefined,
        type: type = Undefined,
        ui_disable_button: bool = Undefined,
        ui_disable_other: Any = Undefined,
        ui_disable_self: Any = Undefined,
        ui_file_filter: str | None = Undefined,
        ui_flags: UIFlags | list[UIFlags] = Undefined,
        ui_group: Union[str, Hashable, list[Hashable]] = Undefined,
        ui_group_parent: UIGroups | list[UIGroups] = Undefined,
        ui_info: GUIMessage = Undefined,
        ui_invalid_input: GUIMessage = Undefined,
        ui_show_dir_only: bool = Undefined,
        ui_type: UITypes = Undefined,
        ui_unit: str = Undefined,
        validators: Callable | list[Callable] = Undefined,
        values: list | dict = Undefined,
    ):
        """
        Create an option instance usable in a GUI environment.

        An Option is the value of a setting, as defined in the template specification.

        Parameters
        ----------
        default : Any
            The default value for this setting.
            ##### Applicable settings: All
        actions : Callable | list[Callable], optional
            Functions to call when this setting changes value.
            Each function must take one argument, which is the new value of this setting.
            ##### Applicable settings: All
        max : Number, optional
            The maximum value for this setting.
            If None, there is no limit (though upper limit is 999999 in the GUI).
            ##### Applicable settings: Any number ranges (e.g. slider or spinbox)
            NOTE: Sliders do not support floats currently.
        min : Number, optional
            The minimum value for this setting.
            If None, there is no limit (though lower limit is 999999 in the GUI).
            ##### Applicable settings: Any number ranges (e.g. slider or spinbox)
            NOTE: Sliders do not support floats currently.
        type : type, optional
            The Python type for the value of this setting. For instance, 3 has type 'int'.
            ##### Applicable settings: All
            NOTE: Types are also inferred from other arguments.
        ui_disable_button : bool, optional
            Enable or disable the disable button for this setting.
            ##### Applicable settings: All
            NOTE: A disable button is generated by default if `ui_disable_self` is defined.
            NOTE: If `ui_disable_self` is Undefined, the disable button will only disable this setting in the GUI.
        ui_disable_other : Any, optional
            The value which disables children of this setting.
            This value is used in validation if it is the smallest of all other values (e.g. default, min).

            Please ensure that the backend using this setting respects this value - otherwise it has no effect.
            ##### Applicable settings: All
        ui_disable_self : Any, optional
            The value which disables this setting.
            This value is used in validation if it is the smallest of all other values (e.g. default, min).

            Please ensure that the backend using this setting respects this value - otherwise it has no effect.
            In the GUI, a button for disabling this setting is provided.
            ##### Applicable settings: All
        ui_file_filter : str, optional
            Only files matching this filter are shown.
            If None, all files are shown.
            If you want multiple filters, seperate them with ;;

            For instance:
            ```
            "Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"
            ```
            ##### Applicable settings: File Selectors
        ui_flags : UIFlags | list[UIFlags], optional
            Special flags that apply to this setting.
            ##### Applicable settings: All
        ui_group : str | Hashable | list[Hashable], optional
            Designate a group ID (GID) which all options with this GID belongs to.
            This makes various actions possible for settings, e.g., they can be visually grouped in the GUI.

            A valid GID can be either:
            - str: "id_1, id_2 ,..., id_n"
            - Hashable: Any hashable object, e.g. 0
            - list[Hashable]: A list of hashable objects that follows the ordering of a str GID

            The ordering of a str GID is as follows:
            - This setting belongs to the group at id_1.
            - Any subsequent GIDs are children of this setting's group.

            ##### Applicable settings: All
        ui_group_parent : UIGroups | list[UIGroups], optional
            Designate the parent setting of a group.

            All groups must have a parent and only one setting in each group can be designated parent.
            If more than one exist, the first found is used.
            ##### Applicable settings: All
            NOTE: Full documentation is available at #LINK: src\\applib\\module\\configuration\\tools\\template_options\\template_docs.txt
        ui_info : GUIMessage, optional
            The title and description of this setting in the GUI.
            ##### Applicable settings: All
        ui_invalid_input : GUIMessage, optional
            Message informing the user that they typed invalid data into this setting in the GUI.
            ##### Applicable settings: Any free-form input, e.g., a line edit.
        ui_show_dir_only : bool, optional
            Only show directories. `ui_file_filter` is ignored.
            ##### Applicable settings: File Selectors
        ui_type : UITypes, optional
            The widget type to use for this setting.
            ##### Applicable settings: All
        ui_unit : str, optional
            The unit associated with this setting.
            ##### Applicable settings: Slider (TODO: Ensure units can be used on all GUI elements)
            NOTE: Must be singular, i.e., "day".
        validators : Callable | list[Callable], optional
            Functions used to validate the value of this setting (in addition to default Pydantic validation).
            Each function must take one argument, which is the value of this setting.
            If the value is invalid, they must raise either ValueError or AssertionError.
        values : list | dict, optional
            Possible values for this setting.
            ##### Applicable settings: Combobox
        """
        super().__init__(
            default=default,
            actions=actions,
            max=max,
            min=min,
            type=type,
            validators=validators,
        )
        self.ui_disable_button = ui_disable_button
        self.ui_disable_other = ui_disable_other
        self.ui_disable_self = ui_disable_self
        self.ui_file_filter = ui_file_filter
        self.ui_flags = ui_flags
        self.ui_group = ui_group
        self.ui_group_parent = ui_group_parent
        self.ui_info = ui_info
        self.ui_invalid_input = ui_invalid_input
        self.ui_show_dir_only = ui_show_dir_only
        self.ui_type = ui_type
        self.ui_unit = ui_unit
        self.values = values


class FileSelectorOption(GUIOption):
    def __init__(
        self,
        default: str,
        actions: Callable | list[Callable] = Undefined,
        type: type = Undefined,
        ui_disable_button: bool = Undefined,
        ui_disable_other: Any = Undefined,
        ui_disable_self: Any = Undefined,
        ui_file_filter: str | None = None,
        ui_flags: UIFlags | list[UIFlags] = Undefined,
        ui_group: Any | list[Any] = Undefined,
        ui_group_parent: UIGroups | list[UIGroups] = Undefined,
        ui_info: GUIMessage = Undefined,
        ui_show_dir_only: bool = False,
        ui_type: UITypes = UITypes.FILE_SELECTION,
        validators: Callable | list[Callable] = Undefined,
    ):
        super().__init__(
            default=default,
            actions=actions,
            type=type,
            ui_disable_button=ui_disable_button,
            ui_disable_other=ui_disable_other,
            ui_disable_self=ui_disable_self,
            ui_file_filter=ui_file_filter,
            ui_flags=ui_flags,
            ui_group=ui_group,
            ui_group_parent=ui_group_parent,
            ui_info=ui_info,
            ui_show_dir_only=ui_show_dir_only,
            ui_type=ui_type,
            validators=validators,
        )


class ComboBoxOption(GUIOption):
    def __init__(
        self,
        default,
        values: list | dict,
        actions: Callable | list[Callable] = Undefined,
        type: type = Undefined,
        ui_disable_button: bool = Undefined,
        ui_disable_other: Any = Undefined,
        ui_disable_self: Any = Undefined,
        ui_flags: UIFlags | list[UIFlags] = Undefined,
        ui_group: Any | list[Any] = Undefined,
        ui_group_parent: UIGroups | list[UIGroups] = Undefined,
        ui_info: GUIMessage = Undefined,
        ui_type: UITypes = UITypes.COMBOBOX,
        validators: Callable | list[Callable] = Undefined,
    ):
        super().__init__(
            default=default,
            values=values,
            actions=actions,
            type=type,
            ui_disable_button=ui_disable_button,
            ui_disable_other=ui_disable_other,
            ui_disable_self=ui_disable_self,
            ui_flags=ui_flags,
            ui_group=ui_group,
            ui_group_parent=ui_group_parent,
            ui_info=ui_info,
            ui_type=ui_type,
            validators=validators,
        )


class TextEditOption(GUIOption):
    def __init__(
        self,
        default: str,
        actions: Callable | list[Callable] = Undefined,
        type: type = Undefined,
        ui_disable_button: bool = Undefined,
        ui_disable_other: Any = Undefined,
        ui_disable_self: Any = Undefined,
        ui_flags: UIFlags | list[UIFlags] = Undefined,
        ui_group: Any | list[Any] = Undefined,
        ui_group_parent: UIGroups | list[UIGroups] = Undefined,
        ui_info: GUIMessage = Undefined,
        ui_invalid_input: GUIMessage = Undefined,
        ui_type: UITypes = UITypes.LINE_EDIT,
        validators: Callable | list[Callable] = Undefined,
    ):
        super().__init__(
            default=default,
            actions=actions,
            type=type,
            ui_disable_button=ui_disable_button,
            ui_disable_other=ui_disable_other,
            ui_disable_self=ui_disable_self,
            ui_flags=ui_flags,
            ui_group=ui_group,
            ui_group_parent=ui_group_parent,
            ui_info=ui_info,
            ui_invalid_input=ui_invalid_input,
            ui_type=ui_type,
            validators=validators,
        )


class NumberOption(GUIOption):
    def __init__(
        self,
        default: Number,
        actions: Callable | list[Callable] = Undefined,
        min: Number = Undefined,
        max: Number = Undefined,
        type: type = Undefined,
        ui_disable_button: bool = Undefined,
        ui_disable_other: Any = Undefined,
        ui_disable_self: Any = Undefined,
        ui_flags: UIFlags | list[UIFlags] = Undefined,
        ui_group: Any | list[Any] = Undefined,
        ui_group_parent: UIGroups | list[UIGroups] = Undefined,
        ui_info: GUIMessage = Undefined,
        ui_type: UITypes = Undefined,
        ui_unit: str = Undefined,
        validators: Callable | list[Callable] = Undefined,
    ):
        super().__init__(
            default=default,
            actions=actions,
            max=max,
            min=min,
            type=type,
            ui_disable_button=ui_disable_button,
            ui_disable_other=ui_disable_other,
            ui_disable_self=ui_disable_self,
            ui_flags=ui_flags,
            ui_group=ui_group,
            ui_group_parent=ui_group_parent,
            ui_info=ui_info,
            ui_type=ui_type,
            ui_unit=ui_unit,
            validators=validators,
        )
