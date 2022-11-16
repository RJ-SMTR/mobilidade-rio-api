from django.contrib import admin
from mobilidade_rio.pontos.models import *

admin.site.register(Agency)
admin.site.register(Calendar)
admin.site.register(CalendarDates)
admin.site.register(Routes)
admin.site.register(Trips)
admin.site.register(Shapes)
admin.site.register(Stops)
admin.site.register(StopTimes)
admin.site.register(Frequencies)
admin.site.site_header = "App QR-Code"


