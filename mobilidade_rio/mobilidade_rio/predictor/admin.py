from django.contrib import admin

from mobilidade_rio.predictor.models import *

admin.site.register(ShapeWithStops)
#admin.site.register(Frequencies)
admin.site.site_header = "App QR-Code predictor"
