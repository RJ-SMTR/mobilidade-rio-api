from os import getenv

from mobilidade_rio.utils.database import check_database_connection
from .base import *

# Django settings

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        "ENGINE": getenv("DB_ENGINE", "django.db.backends.postgresql_psycopg2"),
        "NAME": getenv("DB_NAME", "postgres"),
        "USER": getenv("DB_USER", "postgres"),
        "PASSWORD": getenv("DB_PASSWORD"),
        "HOST": getenv("DB_HOST", "localhost"),
        "PORT": getenv("DB_PORT", "5434"),
    }
}

check_database_connection()
