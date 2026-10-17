import pytest
from django.core.management import call_command
from django.db import IntegrityError, transaction

from apps.catalogos.models import Categoria
from apps.estados.models import Estado


@pytest.mark.django_db
def test_seed_crea_datos_iniciales():
    call_command("seed_catalogos")

    assert Categoria.objects.count() == 5
    assert Estado.objects.count() == 4


@pytest.mark.django_db
def test_seed_es_idempotente():
    call_command("seed_catalogos")
    call_command("seed_catalogos")

    assert Categoria.objects.count() == 5
    assert Estado.objects.count() == 4


@pytest.mark.django_db
def test_modelo_categoria_es_unico():
    Categoria.objects.create(nombre="vías")

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Categoria.objects.create(nombre="vías")


@pytest.mark.django_db
def test_modelo_estado_es_unico():
    Estado.objects.create(codigo="reportado", nombre="Reportado", orden=1)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Estado.objects.create(codigo="reportado", nombre="Reportado", orden=1)
