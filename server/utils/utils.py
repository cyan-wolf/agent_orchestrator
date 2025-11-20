import os

class MissingEnvVarException(Exception): pass


def get_env_raise_if_none(var_name: str) -> str:
    """
    Gets the given environment variable. Raises :py:class:`utils.utils.MissingEnvVarException` if not set.
    """

    value = os.getenv(var_name)

    if value is None:
        raise MissingEnvVarException(f"missing environment variable '{var_name}'")
    else:
        return value

