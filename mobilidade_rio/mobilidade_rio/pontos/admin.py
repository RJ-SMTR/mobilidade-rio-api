from django.contrib import admin
from mobilidade_rio.pontos.models import Agency, Route, Stop, QrCode, Trip, Stop_times

admin.site.register(Agency)
admin.site.register(Route)
admin.site.register(Stop)
admin.site.register(QrCode)
admin.site.register(Trip)
admin.site.register(Stop_times)
admin.site.site_header = "App QR-Code"


