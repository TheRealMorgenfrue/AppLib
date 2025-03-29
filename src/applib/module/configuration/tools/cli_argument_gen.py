from ...tools.types.config import AnyConfig
from ...tools.types.templates import AnyTemplate
from .template_utils.options import GUIOption, Option


class CLIArgumentGenerator:

    def create_arguments(
        config: AnyConfig, template: AnyTemplate, arg_prefix: str = "--"
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
        args = []
        for k, v, pos, ps in config.get_settings():
            v_t = template.find(k, ps, search_mode="strict")  # type: Option | GUIOption
            if not (
                (v_t.defined(v_t.disable_self) and v_t.disable_self != v)
                or (v_t.defined(v_t.ui_disable_self) and v_t.ui_disable_self != v)
            ):
                continue
            args.append(f"{arg_prefix}{v}")
        return args
