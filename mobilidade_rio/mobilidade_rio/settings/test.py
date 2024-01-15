from os import getenv
from .base import *  # pylint: disable=W0401

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': getenv("DB_NAME"),
        'USER': getenv("DB_USER"),
        'PASSWORD': getenv("DB_PASSWORD"),
        'HOST': getenv("DB_HOST"),
        'PORT': getenv("DB_PORT"),
    }
}
