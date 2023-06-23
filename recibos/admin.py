from django.contrib import admin
from .models import Recibo

class ReciboAdmin(admin.ModelAdmin):
    list_display = ['id', 'codigo', 'descripcion', 'monto']
    list_filter = ['monto']
    search_fields = ['codigo', 'descripcion']

admin.site.register(Recibo, ReciboAdmin)

