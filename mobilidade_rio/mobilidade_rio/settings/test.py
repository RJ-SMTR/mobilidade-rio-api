"""
This setting is made to run in your local machine
"""
from .base import *

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': "db.sqlite3",
    },
}
