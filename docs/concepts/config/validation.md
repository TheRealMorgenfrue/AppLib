AppLib performs config validation in multiple stages:

- Stage 1: Internal Pydantic validation
- Stage 2: Option validators
- Stage 3: Missing or superfluous Options
- Stage 4: Option compatibility validation

!!! note

    Usually, you don't have to worry about validation due
    to the automatic type inference employed by AppLib.

This page describes how to configure the validation stages of a [Template](applib.BaseTemplate) class.

## Stage 1: Internal Pydantic validation

The first validation stage is [Pydantic](https://pydantic.dev) validation using type information declared or inferred from an [Option](option.md).

An Option's type is inferred based on the following rules:

1. Use the [type](applib.Option.type) field, if defined.
2. Use the type of the [default](applib.Option.default) field, if defined.
3. If both [type](applib.Option.type) and [default](applib.Option.default) are defined, use the union of both types.

To explicitly declare a type on an Option, use the [type](applib.Option.type) field:

```py
Option(
    type=int
)
```

## Stage 2: Option validators

The second validation stage is validators assigned to an [Option](applib.Option.validators).

A validator is a Python function which takes the value of the Option as argument.
If the value is invalid, the function must raise a ValueError.
If the value is valid, the function must return the value.

Here's an example validator, which checks if a path exist on the computer:

```py
from pathlib import Path

def validate_path(path: str) -> str:
    if not Path(path).exists() and not Path(path).resolve().exists():
        raise ValueError(f"'{path}' does not exist on the filesystem")
    return path
```

A validator can be assigned to an Option like this:

```py
Option(
    validators=validate_path,
)
```

???+ tip

    Multiple validators works too!
    ```py
    Option(
        validators=[validate_path, validate_ip_address],
    )
    ```

## Stage 3: Missing or superfluous Options

check_missing_fields

## Stage 4: Option compatibility validation

The fourth validation stage ensures all values of a [Template](applib.BaseTemplate) are compatible with each other.

For instance, imagine you have two [Option](applib.Option)s, `segment` and `bit_depth`.
The `bit_depth` can be 8 bit or 16 bit, but `segment` does not support 16 bit encoding.
This relationship is captured as follows:

```python
from applib import (
    ComboBoxOption,
    CompatilityValidator,
    GUIMessage,
    Option,
)

from ..runners.compatibility.encoding_compatibility import compatible_bit_depth

"segment": Option(
    default=False,
    ui_info=GUIMessage("Segment the video (background removal)"),
    validators=[
        CompatilityValidator(
            compatible_bit_depth, # <-- Your function, which tests segment and bit_depth
            ["bit_depth"] # <-- Enter the dependencies of `segment`
        )
    ],
),
"bit_depth": ComboBoxOption(
    default="8bit",
    values=["8bit", "16bit"],
    ui_info=GUIMessage("Bit Depth of the raw pipe input to FFmpeg"),
)
```

???+ tip

    You can mix and match any type of validator:

    ```python
    "segment": Option(
        validators=[
            validate_path,
            CompatilityValidator(
                compatible_bit_depth,
                ["bit_depth"]
            ),
            validate_ip_address,
        ],
    ),
    ```

The function `compatible_bit_depth` is one you need to define. It takes as many arguments as there are dependencies in the relationship.
The first argument is the one the function is attached to (in this example `segment`). The function must raise a ValueError if the [Option](applib.Option)s
checked are incompatible.

Here's an example of how `compatible_bit_depth` can look like:

```python
def compatible_bit_depth(segment: bool, bit_depth: str):
    if segment and bit_depth.lower() == "16bit":
        raise ValueError("16bit input is not supported with segmentation")
```
