import os
import sys
# set relative path to server's root
sys.path.append('../../mobilidade_rio')
# ls
# print(os.listdir('.'))
# set variables
os.environ["DJANGO_SETTINGS_MODULE"] = "mobilidade_rio.settings.native"
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
# start django
import django
django.setup()