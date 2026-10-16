import hashlib
import secrets

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import TokenUsuario


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
