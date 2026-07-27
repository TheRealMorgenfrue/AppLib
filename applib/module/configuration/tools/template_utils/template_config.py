from typing import Literal, TypedDict


class TemplateConfig(TypedDict):
    disable_warnings: Literal["gui", "cli", "all"]
    """Disables warnings emitted by the template parser."""
