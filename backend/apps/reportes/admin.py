from django.contrib import admin
from .models import Reporte, FotoReporte

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('folio', 'titulo', 'categoria', 'estado', 'usuario', 'creado_en')
    list_filter = ('estado', 'categoria', 'zona')
    search_fields = ('folio', 'titulo', 'descripcion')

@admin.register(FotoReporte)
class FotoReporteAdmin(admin.ModelAdmin):
    list_display = ('reporte', 'orden', 'clave_almacenamiento')