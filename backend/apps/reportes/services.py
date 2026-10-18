from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import Reporte


def generar_folio():
    anio = timezone.localdate().year
    prefijo = f"AR-{anio}-"
    with transaction.atomic():
        total = Reporte.objects.filter(folio__startswith=prefijo).count()
        return f"{prefijo}{total + 1:06d}"


def enviar_correo_confirmacion_reporte(usuario, reporte):
    mensaje = (
        f"Hola {usuario.nombre or usuario.email},\n\n"
        f"Tu reporte fue registrado con el folio {reporte.folio}.\n\n"
        f"Título: {reporte.titulo}\n"
        f"Categoría: {reporte.categoria.nombre}\n"
        f"Estado: {reporte.estado.nombre}\n"
        f"Descripción: {reporte.descripcion}"
    )
    send_mail(
        subject=f"Reporte registrado: {reporte.folio}",
        message=mensaje,
        from_email=None,
        recipient_list=[usuario.email],
    )
