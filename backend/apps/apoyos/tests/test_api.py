import pytest
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient

from apps.catalogos.models import Categoria
from apps.estados.models import Estado
from apps.reportes.models import Reporte
from apps.reportes.services import generar_folio
from apps.usuarios.models import Usuario

PASSWORD = "Segura123!"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def usuario():
    return Usuario.objects.create_user(
        email="ana@example.com",
        nombre="Ana",
        password=PASSWORD,
        activo=True,
        correo_confirmado=True,
    )


@pytest.fixture
def otro_usuario():
    return Usuario.objects.create_user(
        email="lucas@example.com",
        nombre="Lucas",
        password=PASSWORD,
        activo=True,
        correo_confirmado=True,
    )


@pytest.fixture
def categoria():
    return Categoria.objects.create(nombre="vías", activa=True)


@pytest.fixture
def estado_reportado():
    return Estado.objects.create(
        codigo="reportado", nombre="Reportado", orden=1, es_final=False
    )


def crear_reporte(usuario, categoria, estado):
    return Reporte.objects.create(
        folio=generar_folio(),
        usuario=usuario,
        categoria=categoria,
        estado=estado,
        titulo="Hueco en la vía",
        descripcion="Descripción válida con más de veinte caracteres para reportar.",
        ubicacion=Point(-75.6811, 4.5339, srid=4326),
    )


@pytest.mark.django_db
def test_apoyar_reporte_incrementa_total(
    api_client, usuario, otro_usuario, categoria, estado_reportado
):
    reporte = crear_reporte(usuario, categoria, estado_reportado)
    api_client.force_authenticate(user=otro_usuario)
    resp = api_client.post(f"/api/reportes/{reporte.id}/apoyos/")
    assert resp.status_code == 201
    reporte.refresh_from_db()
    assert reporte.total_apoyos == 1
    assert resp.data["total_apoyos"] == 1


@pytest.mark.django_db
def test_doble_apoyo_devuelve_409(
    api_client, usuario, otro_usuario, categoria, estado_reportado
):
    reporte = crear_reporte(usuario, categoria, estado_reportado)
    api_client.force_authenticate(user=otro_usuario)
    api_client.post(f"/api/reportes/{reporte.id}/apoyos/")
    resp = api_client.post(f"/api/reportes/{reporte.id}/apoyos/")
    assert resp.status_code == 409
    reporte.refresh_from_db()
    assert reporte.total_apoyos == 1


@pytest.mark.django_db
def test_retirar_apoyo_decrementa_total(
    api_client, usuario, otro_usuario, categoria, estado_reportado
):
    reporte = crear_reporte(usuario, categoria, estado_reportado)
    api_client.force_authenticate(user=otro_usuario)
    api_client.post(f"/api/reportes/{reporte.id}/apoyos/")
    resp = api_client.delete(f"/api/reportes/{reporte.id}/apoyos/")
    assert resp.status_code == 204
    reporte.refresh_from_db()
    assert reporte.total_apoyos == 0


@pytest.mark.django_db
def test_retirar_sin_apoyo_devuelve_404(
    api_client, usuario, otro_usuario, categoria, estado_reportado
):
    reporte = crear_reporte(usuario, categoria, estado_reportado)
    api_client.force_authenticate(user=otro_usuario)
    resp = api_client.delete(f"/api/reportes/{reporte.id}/apoyos/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_apoyar_reporte_propio_devuelve_400(
    api_client, usuario, categoria, estado_reportado
):
    reporte = crear_reporte(usuario, categoria, estado_reportado)
    api_client.force_authenticate(user=usuario)
    resp = api_client.post(f"/api/reportes/{reporte.id}/apoyos/")
    assert resp.status_code == 400
    reporte.refresh_from_db()
    assert reporte.total_apoyos == 0


@pytest.mark.django_db
def test_apoyar_sin_auth_devuelve_401(api_client, usuario, categoria, estado_reportado):
    reporte = crear_reporte(usuario, categoria, estado_reportado)
    resp = api_client.post(f"/api/reportes/{reporte.id}/apoyos/")
    assert resp.status_code == 401
