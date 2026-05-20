AppLib performs config validation in multiple stages:

- Stage 1: Internal Pydantic validation
- Stage 2: Option validators
- Stage 3: Missing or superfluous Options
- Stage 4: Option compatibility validation

!!! note

    Usually, you don't have to worry about validation due
    to the automatic type inference employed by AppLib.

This page describes how to configure the validation stages validation of a [Template](applib.BaseTemplate) class.

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
        err_msg = f"'{path}' does not exist on the filesystem"
        raise ValueError(err_msg)
    return path
```

A validator can be assigned to an Option like this:

```py
Option(
    validators=validate_path,
)

# Multiple validators works too!
Option(
    validators=[validate_path, validate_ip_address],
)
```

## Stage 3: Missing or superfluous Options

check_missing_fields

## Stage 4: Option compatibility validation

The fourth stage ensures all values of the Template are compatible with each other.

Sometimes, the value of an [Option](applib.Option) is incompatible with the value of another.
