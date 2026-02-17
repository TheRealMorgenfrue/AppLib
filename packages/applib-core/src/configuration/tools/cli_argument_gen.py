from collections.abc import Iterable
from typing import Any

from ...tools.types.config import AnyConfig
from ...tools.types.templates import AnyTemplate
from ..runners.converters.cmd_converter import CMDConverter
from .template_utils.options import GUIOption, Option


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
        args: Iterable[tuple[str, Any, str]],
        template: AnyTemplate,
        arg_prefix: str = "--",
    ) -> list[str]:
        """
        Create command line arguments from `args` and its associated `template`.

        Parameters
        ----------
        arg_list : list[_rbtm_item]
            A list of `_rbtm_item`s created by a config.
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
            option = template.get_value(
                k, path, search_mode="strict"
            )  # type: Option | GUIOption
            if not (
                (option.defined(option.disable_self) and option.disable_self != v)
                or (
                    option.defined(option.ui_disable_self)
                    and option.ui_disable_self != v
                )
            ):
                continue

            if option.defined(option.converter) and isinstance(
                option.converter, CMDConverter
            ):
                # Convert value to the correct CLI argument
                v = option.converter.getArgument(v)

            out_args.append(f"{arg_prefix}{v}")
        return out_args
