from django.contrib import admin
from mobilidade_rio.pontos.models import Ponto, QrCode

admin.site.register(Ponto)
admin.site.register(QrCode)
admin.site.site_header = "App QR-Code"
