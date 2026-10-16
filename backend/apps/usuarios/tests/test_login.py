from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.usuarios.models import Usuario

PASSWORD = "Segura123!"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def usuario_confirmado():
    return Usuario.objects.create_user(
        email="ana@example.com",
        nombre="Ana",
        password=PASSWORD,
        activo=True,
        correo_confirmado=True,
    )


def login(api_client, email, password):
    return api_client.post(
        "/api/auth/login/", {"email": email, "password": password}, format="json"
    )


@pytest.mark.django_db
def test_login_exitoso_devuelve_access_y_refresh(api_client, usuario_confirmado):
    resp = login(api_client, "ana@example.com", PASSWORD)
    assert resp.status_code == 200
    assert "access" in resp.data
    assert "refresh" in resp.data


@pytest.mark.django_db
def test_login_con_password_incorrecta_falla(api_client, usuario_confirmado):
    resp = login(api_client, "ana@example.com", "MalaClave1!")
    assert resp.status_code == 401
    usuario_confirmado.refresh_from_db()
    assert usuario_confirmado.intentos_fallidos == 1


@pytest.mark.django_db
def test_login_usuario_no_confirmado_falla(api_client):
    Usuario.objects.create_user(
        email="ana@example.com",
        password=PASSWORD,
        activo=True,
        correo_confirmado=False,
    )
    resp = login(api_client, "ana@example.com", PASSWORD)
    assert resp.status_code == 403


@pytest.mark.django_db
def test_login_usuario_inactivo_falla(api_client):
    Usuario.objects.create_user(
        email="ana@example.com",
        password=PASSWORD,
        activo=False,
        correo_confirmado=True,
    )
    resp = login(api_client, "ana@example.com", PASSWORD)
    assert resp.status_code == 403


@pytest.mark.django_db
def test_login_bloqueo_tras_5_intentos(api_client, usuario_confirmado):
    for _ in range(4):
        resp = login(api_client, "ana@example.com", "MalaClave1!")
        assert resp.status_code == 401
    resp = login(api_client, "ana@example.com", "MalaClave1!")
    assert resp.status_code == 403
    usuario_confirmado.refresh_from_db()
    assert usuario_confirmado.bloqueado_hasta is not None
    assert usuario_confirmado.bloqueado_hasta > timezone.now()


@pytest.mark.django_db
def test_login_bloqueado_rechaza_incluso_con_password_correcta(
    api_client, usuario_confirmado
):
    usuario_confirmado.bloqueado_hasta = timezone.now() + timedelta(minutes=15)
    usuario_confirmado.save()
    resp = login(api_client, "ana@example.com", PASSWORD)
    assert resp.status_code == 403


@pytest.mark.django_db
def test_login_exitoso_resetea_intentos_fallidos(api_client, usuario_confirmado):
    usuario_confirmado.intentos_fallidos = 3
    usuario_confirmado.save()
    resp = login(api_client, "ana@example.com", PASSWORD)
    assert resp.status_code == 200
    usuario_confirmado.refresh_from_db()
    assert usuario_confirmado.intentos_fallidos == 0
    assert usuario_confirmado.bloqueado_hasta is None


@pytest.mark.django_db
def test_refresh_devuelve_nuevo_access(api_client, usuario_confirmado):
    login_resp = login(api_client, "ana@example.com", PASSWORD)
    refresh = login_resp.data["refresh"]
    resp = api_client.post("/api/auth/refresh/", {"refresh": refresh}, format="json")
    assert resp.status_code == 200
    assert "access" in resp.data


@pytest.mark.django_db
def test_refresh_con_token_invalido_falla(api_client):
    resp = api_client.post("/api/auth/refresh/", {"refresh": "basura"}, format="json")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_logout_invalida_refresh(api_client, usuario_confirmado):
    login_resp = login(api_client, "ana@example.com", PASSWORD)
    access = login_resp.data["access"]
    refresh = login_resp.data["refresh"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    resp = api_client.post("/api/auth/logout/", {"refresh": refresh}, format="json")
    assert resp.status_code == 200
    api_client.credentials()
    resp = api_client.post("/api/auth/refresh/", {"refresh": refresh}, format="json")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_endpoint_protegido_requiere_token(api_client, usuario_confirmado):
    resp = api_client.get("/api/auth/perfil/")
    assert resp.status_code == 401

    login_resp = login(api_client, "ana@example.com", PASSWORD)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_resp.data['access']}")
    resp = api_client.get("/api/auth/perfil/")
    assert resp.status_code == 200
    assert resp.data["email"] == "ana@example.com"
    assert resp.data["nombre"] == "Ana"
