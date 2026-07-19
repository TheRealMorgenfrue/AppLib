The template class serves as the basis for configuration management in AppLib.

This page describes how to declare and use templates.

## Introduction

As an application developer, you have probably faced one or more of these problems:

1. Your application needs a config file to store user input across application launches.
2. You need to validate the user input to prevent erronous inputs from causing undesired behavior or outright crashing your application.
3. The settings present in the configuration file should be shown to the user. However, you have many settings and do not want to manually code them into the application.

A template solves all of these issues by providing a declarative way to specify your configuration files, with built-in, basic type checking/inference and support for powerful, custom [validation functions](validation.md).
Combined with a [Config](config.md), GUI [generation](../gui/generators.md) and [layout](../gui/layout.md) or CLI [argument parsing](../cli/argument_parsing.md), you can declare a template once and use it effortlessly across CLI, GUI, and on-disk files.

## Definition

A template defines the structure of a config file, but does not store the data of it. This means a template must be paired with a [Config](config.md) to be effective.

A template is a Python dict containing sections (key), settings (key), and [Options](options.md) (value). The dict may be of arbitrary size and depth. It is usually structured as a number of sections containing a number of settings:

```
└─ section_1
   ├─ setting_name_1
   │  └─ Option
   └─ setting_name_2
      └─ Option
└─ section_2
   ├─ setting_name_3
   │  └─ Option
   └─ setting_name_4
      └─ Option
```

??? info "Additional template structures"

    A template may be devoid of sections.
    ```
    ├─ setting_name_1
    │  └─ Option
    └─ setting_name_2
        └─ Option
    ```

    A template may contain subsections, i.e., a section within a section.
    ```
    └─ section_1
       ├─ setting_name_1
       │  └─ Option
       └─ section_2
          └─ setting_name_2
             └─ Option
    ```

    Of course, all template structures can be mixed and matched.

To create your own template, subclass the [BaseTemplate](applib.BaseTemplate) class, as shown below:

```py
from typing import Any, override

from applib import BaseTemplate, GUIMessage, NumberOption


class YourTemplate(BaseTemplate):
    def __init__(self) -> None:
        super().__init__(
            name="Your Template Name",
            template=self._create_template(),
        )

    @override
    def _create_template(self) -> dict[str, Any]:
        return {
            "Process": { # Section name
                "maxThreads": NumberOption( # A setting within the section "Process"
                    default=1,
                    min=1,
                    max=None,
                    ui_info=GUIMessage(
                        "Title",
                        "Description",
                    ),
                ),
            }
        }
```

??? tip "Using the singleton pattern"

    You may use the singleton pattern with your template to create a global instance of it.
    This is very useful for config files used throughout your application.

    The singleton pattern is defined as such:

    ```py
    from typing import Self

    class YourTemplate(BaseTemplate):
        _instance = None

        def __new__(cls) -> Self:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._created = False
            return cls._instance

        def __init__(self) -> None:
            if not self._created:
                super().__init__(
                    name="Your Template Name",
                    template=self._create_template(),
                )
                self._created = True
    ```

    Then, whenever you instantiate the template, like `YourTemplate()`, it always returns the same, global instance.

The template `YourTemplate`, as defined above, produces the following config file (.toml):

```toml
[Process]       # Section "Process"
maxThreads = 1  # Setting "maxThreads"
```
