from .base import *
from os import getenv
from warnings import warn


# Variables

_YELLOW = "\x1b[33;20m"
_RESET = "\x1b[0m"


# Utils

def get_db_envs():
    """
    Check if the environment variables are set and return them.
    If not, show which ones are missing and use default Django values.
    """
    _db_values = {
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "db",
        "PORT": 5432,
    }

    used_envs = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"]
    not_set_envs = [env for env in used_envs if getenv(env) is None]

    # For any existing env, replace default value
    for _env in used_envs:
        env = _env.replace("DB_", "")
        if getenv(env) is not None:
            _db_values[env.replace("DB_", "")] = getenv(env)

    # Warn if any env is not set
    if not_set_envs:
        warn(
f"""{_YELLOW}
Enviroment variables not defined: {not_set_envs}
Using default values.
{_RESET}"""
        , UserWarning, stacklevel=3)

    return _db_values


# Django settings

ALLOWED_HOSTS = ["*"]


db_values = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    },
}
# update base values with envs or defaults
db_values["default"].update(get_db_envs())

DATABASES = db_values