from ...datastructures.redblacktree_mapping import _rbtm_item
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
        return self.create_arguments_from_list(
            config.get_settings(), template, arg_prefix
        )

    def create_arguments_from_list(
        self, arg_list: list[_rbtm_item], template: AnyTemplate, arg_prefix: str = "--"
    ) -> list[str]:
        """
        Create command line arguments from `arg_list` and its associated `template`.

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
        args = []
        for k, v, pos, ps in arg_list:
            option = template.find(
                k, ps, search_mode="strict"
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

            args.append(f"{arg_prefix}{v}")
        return args
