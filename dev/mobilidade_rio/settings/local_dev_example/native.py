"""
This setting is made to run in your local machine
"""
from os import getenv
from mobilidade_rio.settings.base import *  # pylint: disable=W0401,W0614,E0401

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": getenv("DB_ENGINE", "django.db.backends.postgresql_psycopg2"),
        "NAME": getenv("DB_NAME", "postgres"),
        "USER": getenv("DB_USER", "postgres"),
        "PASSWORD": getenv("DB_PASSWORD", "postgres"),
        "HOST": getenv("DB_HOST", "localhost"),
        "PORT": getenv("DB_PORT", "5432"),
    }
}
