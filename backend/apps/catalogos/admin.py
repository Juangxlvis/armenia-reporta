from django.contrib import admin
from .models import Categoria, Zona

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')

@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')