from django.contrib import admin
from .models import Estado, HistorialEstado

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'orden', 'es_final')

@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = ('reporte', 'estado_anterior', 'estado_nuevo', 'cambiado_por', 'cambiado_en')