import os
import sys
# set relative path to server's root
# sys.path.append('')
# ls
# print(os.listdir('.'))
# set variables
os.environ["DJANGO_SETTINGS_MODULE"] = "mobilidade_rio.settings.native"
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
# start django
import django
print("OK")
django.setup()