import pytest
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient

from apps.catalogos.models import Categoria, Zona
from apps.estados.models import Estado, HistorialEstado
from apps.reportes.models import Reporte
from apps.reportes.services import generar_folio
from apps.usuarios.models import Usuario

PASSWORD = "Segura123!"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def funcionario():
    return Usuario.objects.create_user(
        email="funcionario@example.com",
        nombre="Funcionario",
        password=PASSWORD,
        rol=Usuario.ROL_FUNCIONARIO,
        activo=True,
        correo_confirmado=True,
    )


@pytest.fixture
def ciudadano():
    return Usuario.objects.create_user(
        email="ciudadano@example.com",
        nombre="Ciudadano",
        password=PASSWORD,
        rol=Usuario.ROL_CIUDADANO,
        activo=True,
        correo_confirmado=True,
    )


@pytest.fixture
def categoria():
    return Categoria.objects.create(nombre="vías", activa=True)


@pytest.fixture
def estados():
    return {
        "reportado": Estado.objects.create(
            id=1, codigo="reportado", nombre="Reportado", orden=1, es_final=False
        ),
        "en_revision": Estado.objects.create(
            id=2, codigo="en_revision", nombre="En revisión", orden=2, es_final=False
        ),
        "en_proceso": Estado.objects.create(
            id=3, codigo="en_proceso", nombre="En proceso", orden=3, es_final=False
        ),
        "solucionado": Estado.objects.create(
            id=4, codigo="solucionado", nombre="Solucionado", orden=4, es_final=True
        ),
    }


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
def test_listar_reportes_como_funcionario_ok(
    api_client, funcionario, ciudadano, categoria, estados
):
    reporte = crear_reporte(ciudadano, categoria, estados["reportado"])
    api_client.force_authenticate(user=funcionario)
    resp = api_client.get("/api/admin/reportes/")
    assert resp.status_code == 200
    folios = [r["folio"] for r in resp.data]
    assert reporte.folio in folios
    item = next(r for r in resp.data if r["folio"] == reporte.folio)
    assert item["estado_id"] == estados["reportado"].id


@pytest.mark.django_db
def test_listar_reportes_como_ciudadano_falla(
    api_client, ciudadano, categoria, estados
):
    crear_reporte(ciudadano, categoria, estados["reportado"])
    api_client.force_authenticate(user=ciudadano)
    resp = api_client.get("/api/admin/reportes/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_listar_reportes_filtro_busqueda(
    api_client, funcionario, ciudadano, categoria, estados
):
    reporte = crear_reporte(ciudadano, categoria, estados["reportado"])
    otro = Reporte.objects.create(
        folio=generar_folio(),
        usuario=ciudadano,
        categoria=categoria,
        estado=estados["reportado"],
        titulo="Basura acumulada en el parque",
        descripcion="Descripción válida con más de veinte caracteres para reportar.",
        ubicacion=Point(-75.6811, 4.5339, srid=4326),
    )

    api_client.force_authenticate(user=funcionario)
    resp = api_client.get("/api/admin/reportes/", {"search": "basura"})

    assert resp.status_code == 200
    folios = [r["folio"] for r in resp.data]
    assert otro.folio in folios
    assert reporte.folio not in folios


@pytest.mark.django_db
def test_listar_reportes_filtro_estado(
    api_client, funcionario, ciudadano, categoria, estados
):
    reporte = crear_reporte(ciudadano, categoria, estados["reportado"])
    en_proceso = Reporte.objects.create(
        folio=generar_folio(),
        usuario=ciudadano,
        categoria=categoria,
        estado=estados["en_proceso"],
        titulo="Hueco en la vía 2",
        descripcion="Descripción válida con más de veinte caracteres para reportar.",
        ubicacion=Point(-75.6811, 4.5339, srid=4326),
    )

    api_client.force_authenticate(user=funcionario)
    resp = api_client.get(
        "/api/admin/reportes/", {"estado": estados["en_proceso"].id}
    )

    assert resp.status_code == 200
    folios = [r["folio"] for r in resp.data]
    assert en_proceso.folio in folios
    assert reporte.folio not in folios


@pytest.mark.django_db
def test_listar_reportes_filtro_categoria(
    api_client, funcionario, ciudadano, categoria, estados
):
    otra_categoria = Categoria.objects.create(nombre="residuos", activa=True)
    reporte = crear_reporte(ciudadano, categoria, estados["reportado"])
    de_residuos = Reporte.objects.create(
        folio=generar_folio(),
        usuario=ciudadano,
        categoria=otra_categoria,
        estado=estados["reportado"],
        titulo="Hueco en la vía 2",
        descripcion="Descripción válida con más de veinte caracteres para reportar.",
        ubicacion=Point(-75.6811, 4.5339, srid=4326),
    )

    api_client.force_authenticate(user=funcionario)
    resp = api_client.get("/api/admin/reportes/", {"categoria": otra_categoria.id})

    assert resp.status_code == 200
    folios = [r["folio"] for r in resp.data]
    assert de_residuos.folio in folios
    assert reporte.folio not in folios


@pytest.mark.django_db
def test_listar_reportes_filtro_zona(
    api_client, funcionario, ciudadano, categoria, estados
):
    zona = Zona.objects.create(nombre="Centenario", activa=True)
    reporte = crear_reporte(ciudadano, categoria, estados["reportado"])
    de_zona = Reporte.objects.create(
        folio=generar_folio(),
        usuario=ciudadano,
        categoria=categoria,
        estado=estados["reportado"],
        zona=zona,
        titulo="Hueco en la vía 2",
        descripcion="Descripción válida con más de veinte caracteres para reportar.",
        ubicacion=Point(-75.6811, 4.5339, srid=4326),
    )

    api_client.force_authenticate(user=funcionario)
    resp = api_client.get("/api/admin/reportes/", {"zona": zona.id})

    assert resp.status_code == 200
    folios = [r["folio"] for r in resp.data]
    assert de_zona.folio in folios
    assert reporte.folio not in folios


@pytest.mark.django_db
def test_cambiar_estado_ok(api_client, funcionario, ciudadano, categoria, estados):
    reporte = crear_reporte(ciudadano, categoria, estados["reportado"])
    api_client.force_authenticate(user=funcionario)
    resp = api_client.patch(
        f"/api/admin/reportes/{reporte.id}/estado/",
        {"estado_id": estados["en_revision"].id, "comentario": "En revisión"},
        format="json",
    )
    assert resp.status_code == 200
    reporte.refresh_from_db()
    assert reporte.estado_id == estados["en_revision"].id

    historial = HistorialEstado.objects.filter(reporte=reporte).order_by("id")
    assert historial.count() == 1
    entrada = historial.last()
    assert entrada.estado_anterior_id == estados["reportado"].id
    assert entrada.estado_nuevo_id == estados["en_revision"].id
    assert entrada.cambiado_por == funcionario
    assert entrada.comentario == "En revisión"


@pytest.mark.django_db
def test_cambiar_estado_requiere_comentario(
    api_client, funcionario, ciudadano, categoria, estados
):
    reporte = crear_reporte(ciudadano, categoria, estados["reportado"])
    api_client.force_authenticate(user=funcionario)
    resp = api_client.patch(
        f"/api/admin/reportes/{reporte.id}/estado/",
        {"estado_id": estados["en_revision"].id},
        format="json",
    )
    assert resp.status_code == 400
    reporte.refresh_from_db()
    assert reporte.estado_id == estados["reportado"].id


@pytest.mark.django_db
def test_cambiar_estado_transicion_invalida_falla(
    api_client, funcionario, ciudadano, categoria, estados
):
    reporte = crear_reporte(ciudadano, categoria, estados["reportado"])
    api_client.force_authenticate(user=funcionario)
    resp = api_client.patch(
        f"/api/admin/reportes/{reporte.id}/estado/",
        {"estado_id": estados["solucionado"].id, "comentario": "Saltando estados"},
        format="json",
    )
    assert resp.status_code == 400
    reporte.refresh_from_db()
    assert reporte.estado_id == estados["reportado"].id


@pytest.mark.django_db
def test_cambiar_estado_a_solucionado_marca_resuelto_en(
    api_client, funcionario, ciudadano, categoria, estados
):
    reporte = crear_reporte(ciudadano, categoria, estados["en_proceso"])
    api_client.force_authenticate(user=funcionario)
    resp = api_client.patch(
        f"/api/admin/reportes/{reporte.id}/estado/",
        {"estado_id": estados["solucionado"].id, "comentario": "Resuelto"},
        format="json",
    )
    assert resp.status_code == 200
    reporte.refresh_from_db()
    assert reporte.estado_id == estados["solucionado"].id
    assert reporte.resuelto_en is not None
