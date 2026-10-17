import pytest
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient

from apps.catalogos.models import Categoria
from apps.estados.models import Estado
from apps.reportes.models import Reporte
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
def estado_reportado():
    return Estado.objects.create(
        codigo="reportado", nombre="Reportado", orden=1, es_final=False
    )


def payload(categoria, **overrides):
    datos = {
        "titulo": "Hueco en la vía principal",
        "descripcion": "Hay un hueco grande que daña los carros todos los días.",
        "categoria": categoria.id,
        "lat": 4.5339,
        "lng": -75.6811,
    }
    datos.update(overrides)
    return datos


@pytest.mark.django_db
def test_crear_reporte_exitoso(api_client, usuario, categoria, estado_reportado):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post("/api/reportes/", payload(categoria), format="json")
    assert resp.status_code == 201
    reporte = Reporte.objects.get()
    assert reporte.estado.codigo == "reportado"
    assert reporte.total_apoyos == 0
    assert reporte.usuario == usuario


@pytest.mark.django_db
def test_crear_reporte_sin_auth_falla(api_client, categoria):
    resp = api_client.post("/api/reportes/", payload(categoria), format="json")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_crear_reporte_descripcion_corta_falla(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post(
        "/api/reportes/",
        payload(categoria, descripcion="x" * 19),
        format="json",
    )
    assert resp.status_code == 400
    assert Reporte.objects.count() == 0


@pytest.mark.django_db
def test_crear_reporte_sin_titulo_falla(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    datos = payload(categoria)
    datos.pop("titulo")
    resp = api_client.post("/api/reportes/", datos, format="json")
    assert resp.status_code == 400
    assert Reporte.objects.count() == 0


@pytest.mark.django_db
def test_crear_reporte_categoria_invalida_falla(api_client, usuario, estado_reportado):
    api_client.force_authenticate(user=usuario)
    datos = {
        "titulo": "Hueco en la vía principal",
        "descripcion": "Hay un hueco grande que daña los carros todos los días.",
        "categoria": 9999,
        "lat": 4.5339,
        "lng": -75.6811,
    }
    resp = api_client.post("/api/reportes/", datos, format="json")
    assert resp.status_code == 400
    assert Reporte.objects.count() == 0


@pytest.mark.django_db
def test_crear_reporte_asigna_estado_inicial(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post("/api/reportes/", payload(categoria), format="json")
    assert resp.status_code == 201
    assert Reporte.objects.get().estado.codigo == "reportado"


@pytest.mark.django_db
def test_crear_reporte_guarda_ubicacion_correctamente(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post("/api/reportes/", payload(categoria), format="json")
    assert resp.status_code == 201
    reporte = Reporte.objects.get()
    assert reporte.ubicacion.srid == 4326
    assert reporte.ubicacion.x == -75.6811
    assert reporte.ubicacion.y == 4.5339
    assert reporte.ubicacion.equals(Point(-75.6811, 4.5339, srid=4326))


@pytest.mark.django_db
def test_crear_reporte_no_permite_sobrescribir_estado(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post(
        "/api/reportes/",
        payload(categoria, estado="Solucionado"),
        format="json",
    )
    assert resp.status_code == 201
    assert Reporte.objects.get().estado.codigo == "reportado"
