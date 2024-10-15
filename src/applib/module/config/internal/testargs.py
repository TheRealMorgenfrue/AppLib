from ...tools.decorators import makeAppArgs


@makeAppArgs
class TestArgs:
    # General
    app_version = "1.6.7"
    is_release = False
    traceback_limit = 0 if is_release else None
