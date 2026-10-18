import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.catalogos.models import Categoria


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def categorias_sembradas(db):
    call_command("seed_catalogos")


@pytest.mark.django_db
def test_listar_categorias_publico(api_client, categorias_sembradas):
    resp = api_client.get("/api/categorias/")
    assert resp.status_code == 200
    assert len(resp.data) == 5
    assert [c["nombre"] for c in resp.data] == [
        "alumbrado",
        "espacio público",
        "residuos",
        "señalización",
        "vías",
    ]


@pytest.mark.django_db
def test_listar_categorias_solo_activas(api_client, categorias_sembradas):
    Categoria.objects.create(nombre="inactiva", activa=False)
    resp = api_client.get("/api/categorias/")
    assert resp.status_code == 200
    assert len(resp.data) == 5
    nombres = {c["nombre"] for c in resp.data}
    assert "inactiva" not in nombres
