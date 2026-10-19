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
def categoria():
    return Categoria.objects.create(nombre="vías", activa=True)


@pytest.fixture
def categoria_alumbrado():
    return Categoria.objects.create(nombre="alumbrado", activa=True)


@pytest.fixture
def estado_reportado():
    return Estado.objects.create(
        codigo="reportado", nombre="Reportado", orden=1, es_final=False
    )


@pytest.fixture
def estado_en_revision():
    return Estado.objects.create(
        codigo="en_revision", nombre="En revisión", orden=2, es_final=False
    )


def crear_reporte(usuario, categoria, estado, titulo, lat, lng):
    return Reporte.objects.create(
        folio=generar_folio(),
        usuario=usuario,
        categoria=categoria,
        estado=estado,
        titulo=titulo,
        descripcion="Descripción válida con más de veinte caracteres para reportar.",
        ubicacion=Point(lng, lat, srid=4326),
    )


@pytest.mark.django_db
def test_mapa_reporte_publico_sin_auth(
    api_client, usuario, categoria, estado_reportado
):
    crear_reporte(
        usuario, categoria, estado_reportado, "Hueco en la vía", 4.5339, -75.6811
    )
    resp = api_client.get("/api/mapa/reportes/")
    assert resp.status_code == 200
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_mapa_reporte_campos_correctos(
    api_client, usuario, categoria, estado_reportado
):
    reporte = crear_reporte(
        usuario, categoria, estado_reportado, "Hueco en la vía", 4.5339, -75.6811
    )
    resp = api_client.get("/api/mapa/reportes/")
    assert resp.status_code == 200
    dato = resp.data[0]
    assert dato["id"] == reporte.id
    assert dato["folio"] == reporte.folio
    assert dato["titulo"] == "Hueco en la vía"
    assert dato["resumen"] == reporte.descripcion[:100]
    assert dato["lat"] == 4.5339
    assert dato["lng"] == -75.6811
    assert dato["estado_id"] == estado_reportado.id
    assert dato["estado_nombre"] == "Reportado"
    assert dato["categoria_id"] == categoria.id
    assert dato["categoria_nombre"] == "vías"
    assert dato["total_apoyos"] == 0
    assert dato["primera_foto"] is None


@pytest.mark.django_db
def test_mapa_filtra_por_categoria(
    api_client, usuario, categoria, categoria_alumbrado, estado_reportado
):
    crear_reporte(
        usuario, categoria, estado_reportado, "Hueco en la vía", 4.5339, -75.6811
    )
    crear_reporte(
        usuario,
        categoria_alumbrado,
        estado_reportado,
        "Lámpara dañada",
        4.5340,
        -75.6810,
    )
    resp = api_client.get(f"/api/mapa/reportes/?categoria={categoria.id}")
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]["categoria_id"] == categoria.id


@pytest.mark.django_db
def test_mapa_filtra_por_estado(
    api_client, usuario, categoria, estado_reportado, estado_en_revision
):
    crear_reporte(
        usuario, categoria, estado_reportado, "Hueco en la vía", 4.5339, -75.6811
    )
    crear_reporte(
        usuario, categoria, estado_en_revision, "Lámpara dañada", 4.5340, -75.6810
    )
    resp = api_client.get(f"/api/mapa/reportes/?estado={estado_en_revision.id}")
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]["estado_id"] == estado_en_revision.id


@pytest.mark.django_db
def test_mapa_filtra_por_bbox(api_client, usuario, categoria, estado_reportado):
    dentro = crear_reporte(
        usuario, categoria, estado_reportado, "Hueco en el centro", 4.5339, -75.6811
    )
    crear_reporte(usuario, categoria, estado_reportado, "Lejos", 4.0, -76.0)
    bbox = "-75.70,4.52,-75.66,4.55"
    resp = api_client.get(f"/api/mapa/reportes/?bbox={bbox}")
    assert resp.status_code == 200
    assert [r["id"] for r in resp.data] == [dentro.id]
