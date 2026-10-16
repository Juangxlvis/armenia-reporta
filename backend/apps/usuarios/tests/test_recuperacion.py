import hashlib
import re
from datetime import timedelta

import pytest
from django.core import mail
from django.utils import timezone
from rest_framework.test import APIClient

from apps.usuarios.models import TokenUsuario, Usuario

PASSWORD = "Segura123!"
NUEVA_PASSWORD = "NuevaSegura456!"


@pytest.fixture
def api_client():
    return APIClient()


def crear_usuario_confirmado(email="ana@example.com", password=PASSWORD):
    return Usuario.objects.create_user(
        email=email,
        nombre="Ana",
        password=password,
        activo=True,
        correo_confirmado=True,
    )


def extraer_token(mensaje):
    match = re.search(r"token=([A-Za-z0-9_-]+)", mensaje.body)
    assert match, "El correo no contiene un enlace con token"
    return match.group(1)


def solicitar_recuperacion(api_client, email):
    return api_client.post("/api/auth/recuperar/", {"email": email}, format="json")


def restablecer(api_client, token, password=NUEVA_PASSWORD):
    return api_client.post(
        "/api/auth/restablecer/",
        {"token": token, "password": password},
        format="json",
    )


def login(api_client, email, password):
    return api_client.post(
        "/api/auth/login/", {"email": email, "password": password}, format="json"
    )


@pytest.mark.django_db
def test_recuperar_envia_correo_con_token(api_client):
    crear_usuario_confirmado()
    resp = solicitar_recuperacion(api_client, "ana@example.com")
    assert resp.status_code == 200
    assert len(mail.outbox) == 1
    assert extraer_token(mail.outbox[0])


@pytest.mark.django_db
def test_recuperar_crea_token_recuperacion(api_client):
    crear_usuario_confirmado()
    resp = solicitar_recuperacion(api_client, "ana@example.com")
    assert resp.status_code == 200
    token_db = TokenUsuario.objects.get(
        usuario__email="ana@example.com", tipo="recuperacion"
    )
    assert token_db.usado_en is None
    assert (
        timedelta(minutes=14)
        < (token_db.expira_en - timezone.now())
        < timedelta(minutes=16)
    )
    plano = extraer_token(mail.outbox[0])
    assert token_db.token == hashlib.sha256(plano.encode()).hexdigest()
    assert token_db.token != plano


@pytest.mark.django_db
def test_recuperar_con_email_inexistente_devuelve_200(api_client):
    resp = solicitar_recuperacion(api_client, "nadie@example.com")
    assert resp.status_code == 200
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_recuperar_con_usuario_no_confirmado_devuelve_200_sin_correo(api_client):
    Usuario.objects.create_user(
        email="ana@example.com",
        nombre="Ana",
        password=PASSWORD,
        activo=True,
        correo_confirmado=False,
    )
    resp = solicitar_recuperacion(api_client, "ana@example.com")
    assert resp.status_code == 200
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_restablecer_con_token_valido_cambia_password(api_client):
    usuario = crear_usuario_confirmado()
    solicitar_recuperacion(api_client, "ana@example.com")
    plano = extraer_token(mail.outbox[0])

    resp = restablecer(api_client, plano)
    assert resp.status_code == 200

    token_db = TokenUsuario.objects.get(usuario=usuario, tipo="recuperacion")
    assert token_db.usado_en is not None

    assert login(api_client, "ana@example.com", NUEVA_PASSWORD).status_code == 200


@pytest.mark.django_db
def test_restablecer_con_token_expirado_falla(api_client):
    usuario = crear_usuario_confirmado()
    plano = "token-expirado"
    TokenUsuario.objects.create(
        usuario=usuario,
        tipo="recuperacion",
        token=hashlib.sha256(plano.encode()).hexdigest(),
        expira_en=timezone.now() - timedelta(minutes=1),
    )
    resp = restablecer(api_client, plano)
    assert resp.status_code == 400


@pytest.mark.django_db
def test_restablecer_con_token_usado_falla(api_client):
    usuario = crear_usuario_confirmado()
    plano = "token-usado"
    TokenUsuario.objects.create(
        usuario=usuario,
        tipo="recuperacion",
        token=hashlib.sha256(plano.encode()).hexdigest(),
        expira_en=timezone.now() + timedelta(minutes=15),
        usado_en=timezone.now(),
    )
    resp = restablecer(api_client, plano)
    assert resp.status_code == 400


@pytest.mark.django_db
def test_restablecer_con_password_debil_falla(api_client):
    usuario = crear_usuario_confirmado()
    plano = "token-valido"
    TokenUsuario.objects.create(
        usuario=usuario,
        tipo="recuperacion",
        token=hashlib.sha256(plano.encode()).hexdigest(),
        expira_en=timezone.now() + timedelta(minutes=15),
    )
    resp = restablecer(api_client, plano, password="123")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_restablecer_token_no_sirve_dos_veces(api_client):
    crear_usuario_confirmado()
    solicitar_recuperacion(api_client, "ana@example.com")
    plano = extraer_token(mail.outbox[0])

    assert restablecer(api_client, plano).status_code == 200
    resp = restablecer(api_client, plano)
    assert resp.status_code == 400


@pytest.mark.django_db
def test_login_con_password_vieja_falla(api_client):
    crear_usuario_confirmado()
    solicitar_recuperacion(api_client, "ana@example.com")
    plano = extraer_token(mail.outbox[0])

    assert restablecer(api_client, plano).status_code == 200
    assert login(api_client, "ana@example.com", PASSWORD).status_code == 401
