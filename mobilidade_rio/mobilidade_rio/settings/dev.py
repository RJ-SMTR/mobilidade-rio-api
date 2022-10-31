from .base import *
from os import getenv

ALLOWED_HOSTS = ["*"]

DATABASES = {
    # TODO: usar variáveis globais quando o Docker conseguir definir
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "postgres",  #getenv("DB_NAME"),
        'USER': "postgres",  #getenv("DB_USER"),
        'PASSWORD': "postgres",  #getenv("DB_PASSWORD"),
        'HOST': "db",  #getenv("DB_HOST"),
        'PORT': 5432,  #getenv("DB_PORT"),
    },
}
