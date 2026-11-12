from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, TokenUsuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'nombre', 'rol', 'activo', 'correo_confirmado')
    list_filter = ('rol', 'activo', 'correo_confirmado')
    search_fields = ('email', 'nombre')
    ordering = ('email',)
    
    # Ajustamos los fieldsets para nuestro modelo personalizado
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('nombre', 'telefono')}),
        ('Permisos', {'fields': ('rol', 'activo', 'correo_confirmado', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'password1', 'password2', 'rol'),
        }),
    )

@admin.register(TokenUsuario)
class TokenUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'expira_en', 'usado_en')