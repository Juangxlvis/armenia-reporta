import re

import pytest
from django.core import mail
from django.utils import timezone
from rest_framework.test import APIClient

from apps.catalogos.models import Categoria
from apps.estados.models import Estado
from apps.usuarios.models import Usuario

PASSWORD = "Segura123!"
PATRON_FOLIO = re.compile(r"^AR-\d{4}-\d{6}$")


@pytest.fixture(autouse=True)
def configurar_correo_locmem(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    mail.outbox.clear()


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
def test_crear_reporte_genera_folio_unico(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post("/api/reportes/", payload(categoria), format="json")
    assert resp.status_code == 201
    assert "folio" in resp.data
    assert PATRON_FOLIO.match(resp.data["folio"])


@pytest.mark.django_db
def test_folio_tiene_formato_correcto(api_client, usuario, categoria, estado_reportado):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post("/api/reportes/", payload(categoria), format="json")
    assert resp.status_code == 201
    assert PATRON_FOLIO.match(resp.data["folio"])


@pytest.mark.django_db
def test_folios_son_unicos(api_client, usuario, categoria, estado_reportado):
    api_client.force_authenticate(user=usuario)
    folios = set()
    for _ in range(3):
        resp = api_client.post("/api/reportes/", payload(categoria), format="json")
        assert resp.status_code == 201
        folios.add(resp.data["folio"])
    assert len(folios) == 3


@pytest.mark.django_db
def test_folio_empieza_en_000001(api_client, usuario, categoria, estado_reportado):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post("/api/reportes/", payload(categoria), format="json")
    assert resp.status_code == 201
    anio = timezone.localdate().year
    assert resp.data["folio"] == f"AR-{anio}-000001"


@pytest.mark.django_db
def test_crear_reporte_envia_correo_con_folio(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post("/api/reportes/", payload(categoria), format="json")
    assert resp.status_code == 201
    assert len(mail.outbox) == 1
    assert resp.data["folio"] in mail.outbox[0].body


@pytest.mark.django_db
def test_correo_se_envia_al_usuario_que_creo_el_reporte(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post("/api/reportes/", payload(categoria), format="json")
    assert resp.status_code == 201
    assert mail.outbox[0].to == [usuario.email]


@pytest.mark.django_db
def test_cliente_no_puede_sobrescribir_folio(
    api_client, usuario, categoria, estado_reportado
):
    api_client.force_authenticate(user=usuario)
    resp = api_client.post(
        "/api/reportes/",
        payload(categoria, folio="AR-1999-999999"),
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["folio"] != "AR-1999-999999"
    assert PATRON_FOLIO.match(resp.data["folio"])
