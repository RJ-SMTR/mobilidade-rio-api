from .base import *
from .utils import get_db_envs

ALLOWED_HOSTS = ["*"]

# remove envs if they are 

db_values = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    },
}
# insert envs or default values
db_values["default"].update(get_db_envs())

DATABASES = db_values
