import pytest
from datetime import timedelta

from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework.test import APIClient

from apps.catalogos.models import Categoria, Zona
from apps.estados.models import Estado
from apps.reportes.models import Reporte
from apps.reportes.services import generar_folio
from apps.usuarios.models import Usuario

PASSWORD = "Segura123!"


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
def test_resumen_publico_devuelve_conteos():
    reportado = Estado.objects.create(
        id=1, codigo="reportado", nombre="Reportado", orden=1, es_final=False
    )
    en_revision = Estado.objects.create(
        id=2, codigo="en_revision", nombre="En revisión", orden=2, es_final=False
    )
    en_proceso = Estado.objects.create(
        id=3, codigo="en_proceso", nombre="En proceso", orden=3, es_final=False
    )
    solucionado = Estado.objects.create(
        id=4, codigo="solucionado", nombre="Solucionado", orden=4, es_final=True
    )
    categoria = Categoria.objects.create(nombre="vías", activa=True)

    ciudadano = Usuario.objects.create_user(
        email="ciudadano@example.com",
        password=PASSWORD,
        rol=Usuario.ROL_CIUDADANO,
    )
    Usuario.objects.create_user(
        email="funcionario@example.com",
        password=PASSWORD,
        rol=Usuario.ROL_FUNCIONARIO,
    )

    crear_reporte(ciudadano, categoria, reportado)
    crear_reporte(ciudadano, categoria, en_revision)
    crear_reporte(ciudadano, categoria, en_proceso)
    crear_reporte(ciudadano, categoria, solucionado)

    resp = APIClient().get("/api/estadisticas/resumen/")

    assert resp.status_code == 200
    assert resp.data == {
        "total_reportes": 4,
        "en_proceso": 2,
        "resueltos": 1,
        "ciudadanos": 1,
    }


@pytest.mark.django_db
def test_por_categoria_publico_devuelve_conteos():
    reportado = Estado.objects.create(
        id=1, codigo="reportado", nombre="Reportado", orden=1, es_final=False
    )
    categoria_vias = Categoria.objects.create(nombre="vías", activa=True)
    categoria_residuos = Categoria.objects.create(nombre="residuos", activa=True)

    ciudadano = Usuario.objects.create_user(
        email="ciudadano@example.com",
        password=PASSWORD,
        rol=Usuario.ROL_CIUDADANO,
    )

    crear_reporte(ciudadano, categoria_vias, reportado)
    crear_reporte(ciudadano, categoria_vias, reportado)
    crear_reporte(ciudadano, categoria_residuos, reportado)

    resp = APIClient().get("/api/estadisticas/por-categoria/")

    assert resp.status_code == 200
    assert resp.data == [
        {"categoria_nombre": "vías", "total": 2},
        {"categoria_nombre": "residuos", "total": 1},
    ]


@pytest.mark.django_db
def test_resumen_filtro_fechas():
    reportado = Estado.objects.create(
        id=1, codigo="reportado", nombre="Reportado", orden=1, es_final=False
    )
    categoria = Categoria.objects.create(nombre="vías", activa=True)
    ciudadano = Usuario.objects.create_user(
        email="ciudadano@example.com",
        password=PASSWORD,
        rol=Usuario.ROL_CIUDADANO,
    )

    viejo = crear_reporte(ciudadano, categoria, reportado)
    crear_reporte(ciudadano, categoria, reportado)

    Reporte.objects.filter(pk=viejo.pk).update(
        creado_en=timezone.now() - timedelta(days=5000)
    )

    resp = APIClient().get("/api/estadisticas/resumen/", {"desde": "2024-01-01"})

    assert resp.status_code == 200
    assert resp.data["total_reportes"] == 1


@pytest.mark.django_db
def test_por_categoria_filtro_fechas():
    reportado = Estado.objects.create(
        id=1, codigo="reportado", nombre="Reportado", orden=1, es_final=False
    )
    categoria_vias = Categoria.objects.create(nombre="vías", activa=True)
    categoria_residuos = Categoria.objects.create(nombre="residuos", activa=True)
    ciudadano = Usuario.objects.create_user(
        email="ciudadano@example.com",
        password=PASSWORD,
        rol=Usuario.ROL_CIUDADANO,
    )

    viejo = crear_reporte(ciudadano, categoria_vias, reportado)
    crear_reporte(ciudadano, categoria_residuos, reportado)

    Reporte.objects.filter(pk=viejo.pk).update(
        creado_en=timezone.now() - timedelta(days=5000)
    )

    resp = APIClient().get("/api/estadisticas/por-categoria/", {"desde": "2024-01-01"})

    assert resp.status_code == 200
    assert resp.data == [{"categoria_nombre": "residuos", "total": 1}]


@pytest.mark.django_db
def test_tiempos_promedio_por_categoria():
    reportado = Estado.objects.create(
        id=1, codigo="reportado", nombre="Reportado", orden=1, es_final=False
    )
    solucionado = Estado.objects.create(
        id=4, codigo="solucionado", nombre="Solucionado", orden=4, es_final=True
    )
    categoria_vias = Categoria.objects.create(nombre="vías", activa=True)
    categoria_residuos = Categoria.objects.create(nombre="residuos", activa=True)
    ciudadano = Usuario.objects.create_user(
        email="ciudadano@example.com",
        password=PASSWORD,
        rol=Usuario.ROL_CIUDADANO,
    )

    r1 = crear_reporte(ciudadano, categoria_vias, solucionado)
    r2 = crear_reporte(ciudadano, categoria_vias, solucionado)
    r3 = crear_reporte(ciudadano, categoria_residuos, solucionado)
    crear_reporte(ciudadano, categoria_vias, reportado)

    ahora = timezone.now()
    Reporte.objects.filter(pk=r1.pk).update(
        creado_en=ahora - timedelta(days=6), resuelto_en=ahora
    )
    Reporte.objects.filter(pk=r2.pk).update(
        creado_en=ahora - timedelta(days=4), resuelto_en=ahora
    )
    Reporte.objects.filter(pk=r3.pk).update(
        creado_en=ahora - timedelta(days=10), resuelto_en=ahora
    )

    resp = APIClient().get("/api/estadisticas/tiempos/")

    assert resp.status_code == 200
    assert resp.data == [
        {"categoria_nombre": "residuos", "promedio_dias": 10.0},
        {"categoria_nombre": "vías", "promedio_dias": 5.0},
    ]


@pytest.mark.django_db
def test_tiempos_filtro_fechas():
    solucionado = Estado.objects.create(
        id=4, codigo="solucionado", nombre="Solucionado", orden=4, es_final=True
    )
    categoria = Categoria.objects.create(nombre="vías", activa=True)
    ciudadano = Usuario.objects.create_user(
        email="ciudadano@example.com",
        password=PASSWORD,
        rol=Usuario.ROL_CIUDADANO,
    )

    viejo = crear_reporte(ciudadano, categoria, solucionado)
    nuevo = crear_reporte(ciudadano, categoria, solucionado)

    ahora = timezone.now()
    Reporte.objects.filter(pk=viejo.pk).update(
        creado_en=ahora - timedelta(days=5000),
        resuelto_en=ahora - timedelta(days=4990),
    )
    Reporte.objects.filter(pk=nuevo.pk).update(
        creado_en=ahora - timedelta(days=2), resuelto_en=ahora
    )

    resp = APIClient().get("/api/estadisticas/tiempos/", {"desde": "2024-01-01"})

    assert resp.status_code == 200
    assert resp.data == [{"categoria_nombre": "vías", "promedio_dias": 2.0}]


@pytest.mark.django_db
def test_zonas_total_reportes():
    reportado = Estado.objects.create(
        id=1, codigo="reportado", nombre="Reportado", orden=1, es_final=False
    )
    categoria = Categoria.objects.create(nombre="vías", activa=True)
    zona_centenario = Zona.objects.create(nombre="Centenario", activa=True)
    zona_norte = Zona.objects.create(nombre="Norte", activa=True)
    ciudadano = Usuario.objects.create_user(
        email="ciudadano@example.com",
        password=PASSWORD,
        rol=Usuario.ROL_CIUDADANO,
    )

    r1 = crear_reporte(ciudadano, categoria, reportado)
    r2 = crear_reporte(ciudadano, categoria, reportado)
    r3 = crear_reporte(ciudadano, categoria, reportado)
    Reporte.objects.filter(pk=r1.pk).update(zona=zona_centenario)
    Reporte.objects.filter(pk=r2.pk).update(zona=zona_centenario)
    Reporte.objects.filter(pk=r3.pk).update(zona=zona_norte)

    resp = APIClient().get("/api/estadisticas/zonas/")

    assert resp.status_code == 200
    assert resp.data == [
        {"zona_nombre": "Centenario", "total_reportes": 2},
        {"zona_nombre": "Norte", "total_reportes": 1},
    ]
