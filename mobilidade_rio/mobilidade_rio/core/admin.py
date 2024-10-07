from django.contrib import admin

from mobilidade_rio.core.models import TableImport

admin.site.register(TableImport)
admin.site.site_header = "Mobilidade Rio"
