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


def crear_reporte(usuario, categoria, estado, titulo):
    return Reporte.objects.create(
        folio=generar_folio(),
        usuario=usuario,
        categoria=categoria,
        estado=estado,
        titulo=titulo,
        descripcion="Descripción válida con más de veinte caracteres para reportar.",
        ubicacion=Point(-75.6811, 4.5339, srid=4326),
    )


@pytest.mark.django_db
def test_mis_reportes_sin_auth_devuelve_401(
    api_client, usuario, categoria, estado_reportado
):
    crear_reporte(usuario, categoria, estado_reportado, "Hueco en la vía")
    resp = api_client.get("/api/reportes/mios/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_mis_reportes_solo_del_usuario(
    api_client, usuario, otro_usuario, categoria, estado_reportado
):
    crear_reporte(usuario, categoria, estado_reportado, "Hueco en la vía")
    crear_reporte(otro_usuario, categoria, estado_reportado, "Lámpara dañada")

    api_client.force_authenticate(user=usuario)
    resp = api_client.get("/api/reportes/mios/")
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]["titulo"] == "Hueco en la vía"


@pytest.mark.django_db
def test_mis_reportes_ordenados_por_creado_desc(
    api_client, usuario, categoria, estado_reportado
):
    primero = crear_reporte(usuario, categoria, estado_reportado, "Primero")
    segundo = crear_reporte(usuario, categoria, estado_reportado, "Segundo")

    api_client.force_authenticate(user=usuario)
    resp = api_client.get("/api/reportes/mios/")
    assert resp.status_code == 200
    titulos = [r["titulo"] for r in resp.data]
    assert titulos == ["Segundo", "Primero"]
    assert {r["id"] for r in resp.data} == {primero.id, segundo.id}
