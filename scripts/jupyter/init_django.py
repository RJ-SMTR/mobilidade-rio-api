import os
import sys
import dotenv

# set relative path to server's root
sys.path.append('../../mobilidade_rio')
# ls
# print(os.listdir('.'))
# set variables
os.environ["DJANGO_SETTINGS_MODULE"] = "mobilidade_rio.settings.native"
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# load env files
# print if env exists
ENV_PATH = '../../../mobilidade_rio/dev_local/api.env'
script_path = os.path.abspath(__file__)
ENV_PATH = os.path.abspath(os.path.join(script_path, ENV_PATH))
dotenv.load_dotenv(dotenv_path=ENV_PATH)

# start django
import django
django.setup()