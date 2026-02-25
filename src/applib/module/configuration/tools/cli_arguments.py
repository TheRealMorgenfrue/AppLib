import shlex
from argparse import ArgumentParser, Namespace, _ArgumentGroup

from pydantic import BaseModel

from applib.module.configuration.tools.search import SearchMode

from ...tools.types.config import AnyConfig
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

    def create_argparser(self, from_config: AnyConfig) -> ArgumentParser:
        """
        Create an argument parser from a config.

        Useful for generating a command-line interface (CLI).

        Parameters
        ----------
        from_config : AnyConfig
            The config to create the argument parser from.

        Returns
        -------
        ArgumentParser
            The argument parser generated from the config.
        """
        parser = ArgumentParser()

        arg_groups: dict[str, _ArgumentGroup] = {}

        for k, _, path in from_config.options():
            groups = path.split("/")
            if len(groups) > 1 and groups[-1] not in arg_groups:
                arg_groups[groups[-1]] = parser.add_argument_group(title=groups[-1])

            option: Option = from_config.template.get_value(
                k, path, mode=SearchMode.STRICT
            )

            try:
                group = arg_groups[groups[-1]]
                # TODO: Help
                group.add_argument(
                    f"--{k}", dest=k, type=option.type, default=option.default
                )
            except (KeyError, IndexError):
                parser.add_argument(
                    f"--{k}", dest=k, type=option.type, default=option.default
                )
        return parser

    def serialize(self, from_config: AnyConfig) -> list[str]:
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

        for k, v, path in from_config.options():
            option: Option = from_config.template.get_value(
                k, path, mode=SearchMode.STRICT
            )

            if option.disable_self:
                continue

            # Must be a bool (not truthy) and must be True
            if v is True:
                args.append(f"--{k}")
            else:
                args.append(f'--{k} "{v}"')

        normalized_str = shlex.join(args)
        return shlex.quote(normalized_str)

    def deserialize(self, args: Namespace, to_model: type[BaseModel]) -> BaseModel:
        """
        Deserialize command-line arguments into a model.

        Parameters
        ----------
        args : Namespace
            The command-line arguments to deserialize.
        to_model : type[BaseModel]
            The model type to deserialize into.

        Returns
        -------
        BaseModel
            An instance of `to_model` with values from `args`.

        Raises
        ------
        ValidationError
            If `args` could not be deserialized into the model.

        """
        # TODO: Handle list[str]
        return to_model(**args)
