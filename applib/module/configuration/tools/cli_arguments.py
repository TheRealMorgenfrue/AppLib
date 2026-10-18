import os
import shlex
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter, _ArgumentGroup
from collections.abc import Mapping, Sequence

from applib.module.configuration.tools.template_utils.template_enums import (
    Flags,
    UITypes,
)

from ...configuration.tools.search import SEARCH_SEP, SearchMode
from ...tools.types.config import AnyConfig
from ...tools.types.templates import AnyTemplate
from .template_utils.options import Option

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

    def _add_template_arguments(self, template: AnyTemplate, parser: ArgumentParser):
        """Add the options of the template to the parser."""
        arg_groups: dict[str, _ArgumentGroup] = {}

        for k, _, path in template.options():
            groups = path.split(SEARCH_SEP)
            if len(groups) > 1 and groups[-1] not in arg_groups:
                arg_groups[groups[-1]] = parser.add_argument_group(groups[-1])

            option: Option = template.get_value(k, path, mode=SearchMode.STRICT)

            if option.defined(option.flags) and Flags.HIDE_IN_CLI in option.flags:  # type: ignore
                continue

            # Add help
            if option.defined(option.ui_info):
                help = f"{option.ui_info.title} (default: %(default)s)\n{option.ui_info.description}"
            else:
                help = "(default: %(default)s)"

            nargs = None
            if not isinstance(option.default, str) and isinstance(
                option.default, (Sequence, Mapping)
            ):
                nargs = "+"

            # Add multiple choices
            choices = None
            if (
                nargs is None
                and option.defined(option.values)
                and isinstance(option.values, list)
            ):
                choices = option.values

            # Add type
            arg_type = None
            if not (
                isinstance(option.default, bool)
                or (option.defined(option.type) and isinstance(option.type, bool))
            ):
                if option.defined(option.type):
                    arg_type = option.type
                elif isinstance(option.default, (Mapping, Sequence)):
                    arg_type = str
                else:
                    arg_type = type(option.default)

            def format(args):
                if len(args) > 3:
                    f = f"\n\t{'\n\t'.join([f'{c}' for c in args])}"
                    metavar = f"{{{f}\n  }}"
                else:
                    f = ", ".join([f"{c}" for c in args])
                    metavar = f"{{{f}}}"
                return metavar

            # Add formatting
            metavar = None
            if isinstance(option.values, Mapping):
                if (
                    option.defined(option.ui_type)
                    and option.ui_type == UITypes.COMBOBOX
                ):
                    metavar = format(option.values.values())
                else:
                    metavar = format(option.values.keys())
            elif choices:
                metavar = format(choices)
            elif option.defined(option.values) and isinstance(option.values, list):
                metavar = format(option.values)
            elif option.defined(option.type):
                metavar = f"{type(option.default) | option.type}"
            else:
                metavar = f"{type(option.default).__name__}"

            # Add actions
            action = None
            if (
                option.defined(option.type)
                and option.type is bool
                or isinstance(option.default, bool)
            ):
                action = "store_true"

            # Assembly argument list
            arguments = {
                "dest": k,
                "default": option.default,
                "metavar": metavar,
                "help": help,
            }
            if action:
                arguments["action"] = action
                arguments.pop("metavar")
            if choices:
                arguments["choices"] = choices
            if arg_type:
                arguments["type"] = arg_type
            if nargs:
                arguments["nargs"] = nargs

            # FIXME: This argument handler cannot handle duplicate keys across sections
            try:
                group = arg_groups[groups[-1]]
                # TODO: Add help
                group.add_argument(
                    f"--{k}",
                    **arguments,
                )
            except (KeyError, IndexError):
                parser.add_argument(
                    f"--{k}",
                    **arguments,
                )

    def create_argparser(
        self,
        from_templates: list[AnyTemplate],
        name: str | None = None,
        version: str = "UNKNOWN VERSION",
    ) -> ArgumentParser:
        """
        Create an argument parser from a template.

        Useful for generating a command-line interface (CLI).

        Parameters
        ----------
        from_templates : list[AnyTemplate]
            The templates to create an argument parser from.
            The first template in the list is the main arg parser, the rest
            are subparsers. The name of the template is the subparsers name, which is given on
            the command line to tell the parsers apart. For instance: `name1 --command 1 name2 --othercommand a`
        name : str, optional
            The program name. If None, the name is automatically inferred. By default None.
        version : str, optional
            The program version. By default `UNKNOWN VERSION`.

        Returns
        -------
        ArgumentParser
            The argument parser generated by `from_value`.
        """
        os.environ["APPLIB_CLIMODE"] = "1"  # Set CLI mode to flush GUI log messages

        if from_templates and not isinstance(from_templates[0], AnyTemplate):
            raise TypeError(
                f"cannot create an argument parser from input '{from_templates}'. Expected an instance of: list[{type(AnyTemplate).__name__}]"
            )

        # TODO: Enable "suggest_on_error=True" in Python 3.14
        # TODO: Add proper "usage" message
        parser = ArgumentParser(
            prog=name,
            usage="%(prog)s [options]",
            formatter_class=RawTextHelpFormatter,
        )
        subparser = None
        parser.add_argument(
            "--version", action="version", version=f"%(prog)s {version}"
        )

        for i, template in enumerate(from_templates):
            if i == 0:
                self._add_template_arguments(template, parser)
                continue

            if subparser is None:
                # FIXME: Subparsers are not supported with argument groups:
                # https://stackoverflow.com/questions/32017020/grouping-argparse-subparser-arguments
                # Instead, try using https://click.palletsprojects.com/en/stable/ instead of argparse
                subparser = parser.add_subparsers()

            t_parser = subparser.add_parser(
                name=template.name,
                description="",  # TODO: Add
                formatter_class=RawTextHelpFormatter,
            )
            self._add_template_arguments(template, t_parser)
        return parser

    def serialize(self, from_config: AnyConfig) -> str:
        """
        Serialize a config to command-line arguments.

        Parameters
        ----------
        from_config : AnyConfig
            The config to serialize.

        Returns
        -------
        list[str]
            A list of shell-escaped command-line arguments.
        """
        args = []

        for k, v, path in from_config:
            try:
                option: Option = from_config.template.get_value(
                    k, path, mode=SearchMode.STRICT
                )
            except KeyError:
                continue

            if option.defined(option.ui_disable_self) and option.ui_disable_self == v:
                continue

            # Must be a bool (not truthy) and must be True
            if v is True:
                args.append(f"--{k}")
            else:
                args.append(f'--{k} "{v}"')

        normalized_str = shlex.join(args)
        return shlex.quote(normalized_str)

    def deserialize(self, args: Namespace, to_config: AnyConfig, merge: bool):
        """
        Deserialize command-line arguments into a config.

        The config's data is overridden with `args`.

        Parameters
        ----------
        args : Namespace
            The command-line arguments to deserialize.
        to_config : type[AnyConfig]
            The model type to deserialize into.
        merge : bool
            If `True`, the command-line arguments are merged into the config.
            Otherwise, a new config is created with default values for
            those not set by command-line args.

        Raises
        ------
        ValidationError
            If `args` could not be deserialized into the model.

        """
        # TODO: Handle list[str]

        if merge:
            to_config.update_config(args)
        else:
            to_config.replace_config(args)
