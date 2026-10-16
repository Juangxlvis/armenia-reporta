import hashlib
import secrets
from datetime import timedelta
from enum import Enum

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import TokenUsuario, Usuario

MAX_INTENTOS_FALLIDOS = 5
DURACION_BLOQUEO = timedelta(minutes=15)


def _hash_token(plano):
    return hashlib.sha256(plano.encode()).hexdigest()


def crear_token(usuario, tipo):
    plano = secrets.token_urlsafe(32)
    TokenUsuario.objects.create(
        usuario=usuario,
        tipo=tipo,
        token=_hash_token(plano),
        expira_en=timezone.now() + TokenUsuario.VIGENCIA[tipo],
    )
    return plano


def enviar_correo_confirmacion(usuario, token):
    enlace = f"{settings.FRONTEND_URL}/auth/confirmar?token={token}"
    mensaje = (
        f"Hola {usuario.nombre or usuario.email},\n\n"
        f"Confirma tu cuenta de Armenia Reporta: {enlace}"
    )
    send_mail(
        subject="Confirma tu cuenta en Armenia Reporta",
        message=mensaje,
        from_email=None,
        recipient_list=[usuario.email],
    )


def enviar_correo_recuperacion(usuario, token):
    enlace = f"{settings.FRONTEND_URL}/auth/restablecer?token={token}"
    mensaje = (
        f"Hola {usuario.nombre or usuario.email},\n\n"
        f"Restablece tu contraseña de Armenia Reporta: {enlace}"
    )
    send_mail(
        subject="Restablece tu contraseña en Armenia Reporta",
        message=mensaje,
        from_email=None,
        recipient_list=[usuario.email],
    )


def usuario_bloqueado(usuario):
    return (
        usuario.bloqueado_hasta is not None and usuario.bloqueado_hasta > timezone.now()
    )


def registrar_intento_fallido(usuario):
    usuario.intentos_fallidos += 1
    if usuario.intentos_fallidos >= MAX_INTENTOS_FALLIDOS:
        usuario.bloqueado_hasta = timezone.now() + DURACION_BLOQUEO
        usuario.intentos_fallidos = 0
        usuario.save()
        return True
    usuario.save()
    return False


def registrar_login_exitoso(usuario):
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    usuario.save()


class ResultadoLogin(Enum):
    EXITO = "exito"
    BLOQUEADO = "bloqueado"
    CREDENCIALES_INVALIDAS = "credenciales_invalidas"
    NO_CONFIRMADO = "no_confirmado"
    INACTIVO = "inactivo"


def iniciar_sesion(email, password):
    usuario = Usuario.objects.filter(email__iexact=email).first()

    if usuario is not None and usuario_bloqueado(usuario):
        return ResultadoLogin.BLOQUEADO, usuario

    if usuario is None or not usuario.check_password(password):
        if usuario is not None and registrar_intento_fallido(usuario):
            return ResultadoLogin.BLOQUEADO, usuario
        return ResultadoLogin.CREDENCIALES_INVALIDAS, usuario

    if not usuario.correo_confirmado:
        return ResultadoLogin.NO_CONFIRMADO, usuario

    if not usuario.activo:
        return ResultadoLogin.INACTIVO, usuario

    registrar_login_exitoso(usuario)
    return ResultadoLogin.EXITO, usuario
