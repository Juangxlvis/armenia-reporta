from rest_framework.permissions import BasePermission

from .models import Usuario


class IsFuncionarioOrAdmin(BasePermission):
    def has_permission(self, request, view):
        usuario = request.user
        return (
            usuario
            and usuario.is_authenticated
            and usuario.rol in (Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMINISTRADOR)
        )
