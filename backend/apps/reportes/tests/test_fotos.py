import io
import random

import pytest
from django.core.files.storage import default_storage
from PIL import Image
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


def imagen_jpeg(ancho=800, alto=600, calidad=90, sigma=100):
    img = Image.effect_noise((ancho, alto), sigma).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=calidad)
    buf.seek(0)
    buf.name = "foto.jpg"
    return buf


def imagen_png(ancho=800, alto=600, transparente=False):
    modo = "RGBA" if transparente else "RGB"
    color = (200, 30, 30, 128) if transparente else (200, 30, 30)
    img = Image.new(modo, (ancho, alto), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    buf.name = "foto.png"
    return buf


def imagen_gif(ancho=10, alto=10):
    img = Image.new("RGB", (ancho, alto), (0, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="GIF")
    buf.seek(0)
    buf.name = "foto.gif"
    return buf


def imagen_grande(ancho=2600, alto=2600):
    datos = random.randbytes(ancho * alto)
    img = Image.frombytes("L", (ancho, alto), datos)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    buf.name = "foto.png"
    return buf


def payload_multipart(categoria, fotos=None):
    datos = {
        "titulo": "Hueco en la vía principal",
        "descripcion": "Hay un hueco grande que daña los carros todos los días.",
        "categoria": str(categoria.id),
        "lat": "4.5339",
        "lng": "-75.6811",
    }
    if fotos is not None:
        datos["fotos"] = fotos
    return datos


def contenido_almacenado(foto):
    with default_storage.open(foto.clave_almacenamiento) as archivo:
        return archivo.read()


@pytest.mark.django_db
def test_crear_reporte_con_una_foto(api_client, usuario, categoria, estado_reportado):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post(
        "/api/reportes/",
        payload_multipart(categoria, fotos=[imagen_jpeg()]),
        format="multipart",
    )
    assert resp.status_code == 201
    reporte = Reporte.objects.get()
    assert reporte.fotos.count() == 1
    foto = reporte.fotos.get()
    assert default_storage.exists(foto.clave_almacenamiento)


@pytest.mark.django_db
def test_crear_reporte_con_tres_fotos(api_client, usuario, categoria, estado_reportado):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post(
        "/api/reportes/",
        payload_multipart(categoria, fotos=[imagen_jpeg() for _ in range(3)]),
        format="multipart",
    )
    assert resp.status_code == 201
    reporte = Reporte.objects.get()
    assert reporte.fotos.count() == 3


@pytest.mark.django_db
def test_crear_reporte_con_cuatro_fotos_falla(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post(
        "/api/reportes/",
        payload_multipart(categoria, fotos=[imagen_jpeg() for _ in range(4)]),
        format="multipart",
    )
    assert resp.status_code == 400
    assert Reporte.objects.count() == 0


@pytest.mark.django_db
def test_crear_reporte_con_foto_mayor_a_5mb_falla(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post(
        "/api/reportes/",
        payload_multipart(categoria, fotos=[imagen_grande()]),
        format="multipart",
    )
    assert resp.status_code == 400
    assert Reporte.objects.count() == 0


@pytest.mark.django_db
def test_crear_reporte_con_formato_invalido_falla(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post(
        "/api/reportes/",
        payload_multipart(categoria, fotos=[imagen_gif()]),
        format="multipart",
    )
    assert resp.status_code == 400
    assert Reporte.objects.count() == 0


@pytest.mark.django_db
def test_crear_reporte_sin_fotos_sigue_funcionando(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    datos = {
        "titulo": "Hueco en la vía principal",
        "descripcion": "Hay un hueco grande que daña los carros todos los días.",
        "categoria": categoria.id,
        "lat": 4.5339,
        "lng": -75.6811,
    }
    resp = api_client.post("/api/reportes/", datos, format="json")
    assert resp.status_code == 201
    reporte = Reporte.objects.get()
    assert reporte.fotos.count() == 0


@pytest.mark.django_db
def test_fotos_se_comprimen(api_client, usuario, categoria, estado_reportado):
    original = imagen_jpeg(ancho=3000, alto=3000, calidad=90, sigma=20)
    tamano_original = len(original.getvalue())

    api_client.force_authenticate(user=usuario)
    resp = api_client.post(
        "/api/reportes/",
        payload_multipart(categoria, fotos=[original]),
        format="multipart",
    )
    assert resp.status_code == 201
    foto = Reporte.objects.get().fotos.get()
    contenido = contenido_almacenado(foto)
    assert len(contenido) < tamano_original
    with Image.open(io.BytesIO(contenido)) as img:
        assert img.width <= 1920
        assert img.height <= 1920


@pytest.mark.django_db
def test_foto_png_se_convierte_a_jpeg(api_client, usuario, categoria, estado_reportado):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post(
        "/api/reportes/",
        payload_multipart(categoria, fotos=[imagen_png()]),
        format="multipart",
    )
    assert resp.status_code == 201
    foto = Reporte.objects.get().fotos.get()
    assert foto.clave_almacenamiento.endswith(".jpg")


@pytest.mark.django_db
def test_fotos_se_ordenan_por_campo_orden(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post(
        "/api/reportes/",
        payload_multipart(categoria, fotos=[imagen_jpeg() for _ in range(3)]),
        format="multipart",
    )
    assert resp.status_code == 201
    ordenes = list(Reporte.objects.get().fotos.values_list("orden", flat=True))
    assert ordenes == [0, 1, 2]
