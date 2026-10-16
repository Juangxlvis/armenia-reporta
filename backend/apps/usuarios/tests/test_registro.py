import hashlib
import re
from datetime import timedelta

import pytest
from django.core import mail
from django.utils import timezone
from rest_framework.test import APIClient

from apps.usuarios.models import TokenUsuario, Usuario


def extraer_token(mensaje):
    match = re.search(r"token=([A-Za-z0-9_-]+)", mensaje.body)
    assert match, "El correo no contiene un enlace con token"
    return match.group(1)


@pytest.fixture
def api_client():
    return APIClient()


DATOS_BASE = {
    "email": "ana@example.com",
    "nombre": "Ana",
    "password": "Segura123!",
    "acepta_datos": True,
}


@pytest.mark.django_db
def test_registro_crea_usuario_inactivo(api_client):
    resp = api_client.post("/api/auth/registro/", DATOS_BASE, format="json")
    assert resp.status_code == 201
    usuario = Usuario.objects.get(email=DATOS_BASE["email"])
    assert usuario.correo_confirmado is False
    assert usuario.acepta_datos_en is not None


@pytest.mark.django_db
def test_registro_email_duplicado_falla(api_client):
    Usuario.objects.create_user(email=DATOS_BASE["email"], password="Segura123!")
    resp = api_client.post("/api/auth/registro/", DATOS_BASE, format="json")
    assert resp.status_code == 400
    assert "email" in resp.data


@pytest.mark.django_db
def test_registro_sin_aceptar_datos_falla(api_client):
    datos = {**DATOS_BASE, "acepta_datos": False}
    resp = api_client.post("/api/auth/registro/", datos, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_registro_password_debil_falla(api_client):
    datos = {**DATOS_BASE, "password": "123"}
    resp = api_client.post("/api/auth/registro/", datos, format="json")
    assert resp.status_code == 400
    assert "password" in resp.data


@pytest.mark.django_db
def test_registro_envia_correo_confirmacion(api_client):
    resp = api_client.post("/api/auth/registro/", DATOS_BASE, format="json")
    assert resp.status_code == 201
    assert len(mail.outbox) == 1
    assert extraer_token(mail.outbox[0])


@pytest.mark.django_db
def test_registro_crea_token_confirmacion(api_client):
    resp = api_client.post("/api/auth/registro/", DATOS_BASE, format="json")
    assert resp.status_code == 201
    token_db = TokenUsuario.objects.get(usuario__email=DATOS_BASE["email"])
    assert token_db.tipo == "confirmacion"
    assert token_db.usado_en is None
    assert (
        timedelta(hours=23)
        < (token_db.expira_en - timezone.now())
        < timedelta(hours=25)
    )
    plano = extraer_token(mail.outbox[0])
    assert token_db.token == hashlib.sha256(plano.encode()).hexdigest()
    assert token_db.token != plano


@pytest.mark.django_db
def test_confirmar_con_token_valido_activa_usuario(api_client):
    api_client.post("/api/auth/registro/", DATOS_BASE, format="json")
    plano = extraer_token(mail.outbox[0])
    resp = api_client.post("/api/auth/confirmar/", {"token": plano}, format="json")
    assert resp.status_code == 200
    usuario = Usuario.objects.get(email=DATOS_BASE["email"])
    assert usuario.correo_confirmado is True
    token_db = TokenUsuario.objects.get(usuario=usuario)
    assert token_db.usado_en is not None


@pytest.mark.django_db
def test_confirmar_con_token_expirado_falla(api_client):
    usuario = Usuario.objects.create_user(
        email=DATOS_BASE["email"], password="Segura123!"
    )
    plano = "token-expirado"
    TokenUsuario.objects.create(
        usuario=usuario,
        tipo="confirmacion",
        token=hashlib.sha256(plano.encode()).hexdigest(),
        expira_en=timezone.now() - timedelta(hours=1),
    )
    resp = api_client.post("/api/auth/confirmar/", {"token": plano}, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_confirmar_con_token_usado_falla(api_client):
    usuario = Usuario.objects.create_user(
        email=DATOS_BASE["email"], password="Segura123!"
    )
    plano = "token-usado"
    TokenUsuario.objects.create(
        usuario=usuario,
        tipo="confirmacion",
        token=hashlib.sha256(plano.encode()).hexdigest(),
        expira_en=timezone.now() + timedelta(hours=24),
        usado_en=timezone.now(),
    )
    resp = api_client.post("/api/auth/confirmar/", {"token": plano}, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_reenviar_confirmacion_genera_nuevo_token(api_client):
    usuario = Usuario.objects.create_user(
        email=DATOS_BASE["email"], password="Segura123!"
    )
    resp = api_client.post(
        "/api/auth/reenviar-confirmacion/", {"email": usuario.email}, format="json"
    )
    assert resp.status_code == 200
    tokens = TokenUsuario.objects.filter(usuario=usuario, tipo="confirmacion")
    assert tokens.count() == 1
    token_db = tokens.first()
    assert token_db.expira_en > timezone.now()
    assert token_db.usado_en is None


@pytest.mark.django_db
def test_reenviar_confirmacion_a_usuario_ya_confirmado_falla(api_client):
    usuario = Usuario.objects.create_user(
        email=DATOS_BASE["email"],
        password="Segura123!",
        correo_confirmado=True,
    )
    resp = api_client.post(
        "/api/auth/reenviar-confirmacion/", {"email": usuario.email}, format="json"
    )
    assert resp.status_code == 400
