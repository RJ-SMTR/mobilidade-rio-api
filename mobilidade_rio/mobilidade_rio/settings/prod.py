from .base import *
from os import getenv
from pathlib import Path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv('SECRET_KEY', 'secret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

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
