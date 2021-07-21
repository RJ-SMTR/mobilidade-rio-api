from django.contrib import admin
from mobilidade_rio.pontos.models import Mode, Stop, QrCode, Linha, Agency, Route, Trip, Sequence

admin.site.register(Mode)
admin.site.register(Stop)
admin.site.register(QrCode)
admin.site.register(Linha)
admin.site.register(Agency)
admin.site.register(Route)
admin.site.register(Trip)
admin.site.register(Sequence)
admin.site.site_header = "App QR-Code"
