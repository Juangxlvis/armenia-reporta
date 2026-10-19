import pytest
from datetime import timedelta
from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework.test import APIClient

from apps.catalogos.models import Categoria
from apps.estados.models import Estado, HistorialEstado
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
        nombre="Ana María",
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


@pytest.fixture
def estado_en_revision():
    return Estado.objects.create(
        codigo="en_revision", nombre="En revisión", orden=2, es_final=False
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


def payload(categoria):
    return {
        "titulo": "Hueco en la vía principal",
        "descripcion": "Hay un hueco grande que daña los carros todos los días.",
        "categoria": categoria.id,
        "lat": 4.5339,
        "lng": -75.6811,
    }


@pytest.mark.django_db
def test_detalle_reporte_sin_auth_devuelve_200(
    api_client, usuario, categoria, estado_reportado
):
    reporte = crear_reporte(usuario, categoria, estado_reportado)
    resp = api_client.get(f"/api/reportes/{reporte.id}/")
    assert resp.status_code == 200
    assert resp.data["folio"] == reporte.folio
    assert resp.data["apoyado_por_mi"] is False


@pytest.mark.django_db
def test_detalle_reporte_con_auth_incluye_apoyado_por_mi(
    api_client, usuario, otro_usuario, categoria, estado_reportado
):
    reporte = crear_reporte(usuario, categoria, estado_reportado)
    api_client.force_authenticate(user=otro_usuario)
    api_client.post(f"/api/reportes/{reporte.id}/apoyos/")

    resp = api_client.get(f"/api/reportes/{reporte.id}/")
    assert resp.status_code == 200
    assert resp.data["apoyado_por_mi"] is True


@pytest.mark.django_db
def test_detalle_reporte_no_existente_devuelve_404(
    api_client, usuario, categoria, estado_reportado
):
    resp = api_client.get("/api/reportes/9999/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_historial_vacio_si_no_hay_entradas(
    api_client, usuario, categoria, estado_reportado
):
    reporte = crear_reporte(usuario, categoria, estado_reportado)
    resp = api_client.get(f"/api/reportes/{reporte.id}/historial/")
    assert resp.status_code == 200
    assert resp.data == []


@pytest.mark.django_db
def test_crear_reporte_genera_historial_inicial(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post("/api/reportes/", payload(categoria), format="json")
    assert resp.status_code == 201
    reporte_id = resp.data["id"]

    resp_hist = api_client.get(f"/api/reportes/{reporte_id}/historial/")
    assert resp_hist.status_code == 200
    assert len(resp_hist.data) == 1
    entrada = resp_hist.data[0]
    assert entrada["estado_anterior_nombre"] is None
    assert entrada["estado_nuevo_nombre"] == "Reportado"


@pytest.mark.django_db
def test_historial_ordenado_por_cambiado_en_asc(
    api_client, usuario, categoria, estado_reportado, estado_en_revision
):
    reporte = crear_reporte(usuario, categoria, estado_reportado)
    ahora = timezone.now()
    h1 = HistorialEstado.objects.create(
        reporte=reporte,
        estado_anterior=None,
        estado_nuevo=estado_reportado,
        cambiado_por=usuario,
        comentario="inicial",
    )
    h2 = HistorialEstado.objects.create(
        reporte=reporte,
        estado_anterior=estado_reportado,
        estado_nuevo=estado_en_revision,
        cambiado_por=usuario,
        comentario="en revision",
    )
    HistorialEstado.objects.filter(pk=h1.pk).update(
        cambiado_en=ahora + timedelta(hours=2)
    )
    HistorialEstado.objects.filter(pk=h2.pk).update(
        cambiado_en=ahora + timedelta(hours=1)
    )

    resp = api_client.get(f"/api/reportes/{reporte.id}/historial/")
    assert resp.status_code == 200
    nombres = [e["estado_nuevo_nombre"] for e in resp.data]
    assert nombres == ["En revisión", "Reportado"]
