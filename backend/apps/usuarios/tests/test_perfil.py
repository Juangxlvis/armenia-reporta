import pytest
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
        telefono="3001234567",
        password=PASSWORD,
        activo=True,
        correo_confirmado=True,
    )


def autenticar(api_client, email="ana@example.com", password=PASSWORD):
    resp = api_client.post(
        "/api/auth/login/", {"email": email, "password": password}, format="json"
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
    return resp


@pytest.mark.django_db
def test_perfil_get_devuelve_campos_completos(api_client, usuario_confirmado):
    autenticar(api_client)
    resp = api_client.get("/api/auth/perfil/")
    assert resp.status_code == 200
    for campo in ("id", "email", "nombre", "telefono", "rol", "creado_en"):
        assert campo in resp.data
    assert resp.data["email"] == "ana@example.com"


@pytest.mark.django_db
def test_perfil_get_requiere_autenticacion(api_client, usuario_confirmado):
    resp = api_client.get("/api/auth/perfil/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_perfil_patch_actualiza_nombre(api_client, usuario_confirmado):
    autenticar(api_client)
    resp = api_client.patch("/api/auth/perfil/", {"nombre": "Ana María"}, format="json")
    assert resp.status_code == 200
    assert resp.data["nombre"] == "Ana María"
    usuario_confirmado.refresh_from_db()
    assert usuario_confirmado.nombre == "Ana María"


@pytest.mark.django_db
def test_perfil_patch_actualiza_telefono(api_client, usuario_confirmado):
    autenticar(api_client)
    resp = api_client.patch(
        "/api/auth/perfil/", {"telefono": "3009876543"}, format="json"
    )
    assert resp.status_code == 200
    assert resp.data["telefono"] == "3009876543"
    usuario_confirmado.refresh_from_db()
    assert usuario_confirmado.telefono == "3009876543"


@pytest.mark.django_db
def test_perfil_patch_actualiza_nombre_y_telefono_a_la_vez(
    api_client, usuario_confirmado
):
    autenticar(api_client)
    resp = api_client.patch(
        "/api/auth/perfil/",
        {"nombre": "Ana María", "telefono": "3009876543"},
        format="json",
    )
    assert resp.status_code == 200
    usuario_confirmado.refresh_from_db()
    assert usuario_confirmado.nombre == "Ana María"
    assert usuario_confirmado.telefono == "3009876543"


@pytest.mark.django_db
def test_perfil_patch_ignora_email(api_client, usuario_confirmado):
    autenticar(api_client)
    resp = api_client.patch(
        "/api/auth/perfil/",
        {"nombre": "X", "email": "otro@test.com"},
        format="json",
    )
    assert resp.status_code == 200
    usuario_confirmado.refresh_from_db()
    assert usuario_confirmado.email == "ana@example.com"


@pytest.mark.django_db
def test_perfil_patch_ignora_rol(api_client, usuario_confirmado):
    autenticar(api_client)
    resp = api_client.patch(
        "/api/auth/perfil/", {"rol": "administrador"}, format="json"
    )
    assert resp.status_code == 200
    usuario_confirmado.refresh_from_db()
    assert usuario_confirmado.rol == "ciudadano"


@pytest.mark.django_db
def test_perfil_patch_ignora_activo_y_confirmado(api_client, usuario_confirmado):
    autenticar(api_client)
    resp = api_client.patch(
        "/api/auth/perfil/",
        {"activo": False, "correo_confirmado": False},
        format="json",
    )
    assert resp.status_code == 200
    usuario_confirmado.refresh_from_db()
    assert usuario_confirmado.activo is True
    assert usuario_confirmado.correo_confirmado is True


@pytest.mark.django_db
def test_perfil_patch_devuelve_objeto_completo(api_client, usuario_confirmado):
    autenticar(api_client)
    resp = api_client.patch("/api/auth/perfil/", {"nombre": "X"}, format="json")
    assert resp.status_code == 200
    for campo in ("id", "email", "nombre", "telefono", "rol", "creado_en"):
        assert campo in resp.data


@pytest.mark.django_db
def test_perfil_patch_con_datos_invalidos_falla(api_client, usuario_confirmado):
    autenticar(api_client)
    resp = api_client.patch("/api/auth/perfil/", {"telefono": "a" * 50}, format="json")
    assert resp.status_code == 400
