from os import getenv
from warnings import warn

_yellow = "\x1b[33;20m"
_reset = "\x1b[0m"

def get_db_envs():
    db_values = {
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "db",
        "PORT": 5432,
    }

    envs = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"]
    not_set_envs = [env for env in envs if getenv(env) is None]

    # For any existing env, replace default value
    for _env in envs:
        env = _env.replace("DB_", "")
        if getenv(env) is not None:
            db_values[env.replace("DB_", "")] = getenv(env)

    # Warn if any env is not set
    if not_set_envs:
        warn(
f"""{_yellow}
Enviroment variables not defined: {not_set_envs}
Using default values.
{_reset}"""
        , UserWarning, stacklevel=3)

    return db_values


# You can test this snippet by running as script
if __name__ == "__main__":
    envs = get_db_envs()
    print(envs)
