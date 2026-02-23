from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel

from ...tools.types.config import AnyConfig
from ...tools.types.templates import AnyTemplate
from .template_utils.options import GUIOption, Option

# TODO: Inspiration from:

# General
# https://docs.pydantic.dev/latest/api/pydantic_settings/#pydantic_settings.CliApp.run
# https://docs.pydantic.dev/latest/concepts/pydantic_settings/#integrating-with-existing-parsers
# https://docs.pydantic.dev/latest/concepts/pydantic_settings/#cli-boolean-flags
# https://docs.pydantic.dev/latest/concepts/pydantic_settings/#cli-boolean-flags


# Serializing
# # https://docs.python.org/3/library/argparse.html#argument-groups
# https://stackoverflow.com/a/72741664 (nice example using serialize to construct argparser)
# https://docs.pydantic.dev/latest/concepts/serialization/#iterating-over-models


# Deserializing
# https://github.com/swansonk14/typed-argument-parser?tab=readme-ov-file#argument-processing
class CLIArguments:
    def __init__(self):
        pass

    def serialize(self, from_config: AnyConfig) -> list[str]:
        pass

    def deserialize(self, args: list[str], to_config: type[AnyConfig]) -> AnyConfig:
        pass


class CLIArgumentGenerator:
    def create_arguments_from_config(
        self, config: AnyConfig, template: AnyTemplate, arg_prefix: str = "--"
    ) -> list[str]:
        """
        Create command line arguments from `config` and its associated `template`.

        Parameters
        ----------
        config : AnyConfig
            The config supplies a value for each argument.
        template : AnyTemplate
            The template determines which arguments are generated.
            NOTE: `config` must be generated from this template.
        arg_prefix : str, optional
            Use this string as argument prefix.
            By default "--".

        Returns
        -------
        list[str]
            A list of command line arguments.
            E.g. ["--a", "--b"]
        """
        return self.create_arguments_from_iter(config.options(), template, arg_prefix)

    def create_arguments_from_iter(
        self,
        args: Iterable[tuple[str, Option, str]],
        template: AnyTemplate,
        arg_prefix: str = "--",
    ) -> list[str]:
        """
        Create command line arguments from `args` and its associated `template`.

        Parameters
        ----------
        arg_list : tuple[str, Option, str]
            A key, its associated Option (or GUIOption), and its path in the mapping.
        template : AnyTemplate
            The template determines which arguments are generated.
            NOTE: `arg_list` must be generated from a config which is from this template.
        arg_prefix : str, optional
            Use this string as argument prefix.
            By default "--".

        Returns
        -------
        list[str]
            A list of command line arguments.
            E.g. ["--a", "--b"]
        """
        out_args = []
        for k, v, path in args:
            option = template.get_value(k, path, search_mode="strict")  # type: Option | GUIOption
            if not (
                (option.defined(option.disable_self) and option.disable_self != v)
                or (
                    option.defined(option.ui_disable_self)
                    and option.ui_disable_self != v
                )
            ):
                continue

            if option.defined(option.converter):
                # Convert value to the correct CLI argument
                cmd = option.converter.getArgument(v)

            out_args.append(f"{arg_prefix}{cmd}")
        return out_args
