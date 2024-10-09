# This exists in an effort to remove circular imports and
# to decouple the logging module from other modules (as much as possible)
class ModuleNames:
    app_name = "AppLib"


class TemplateNames:
    app_template_name = ModuleNames.app_name


class ConfigNames:
    app_config_name = TemplateNames.app_template_name
