import pytest

from apps.usuarios.models import Usuario


@pytest.mark.django_db
def test_create_superuser_con_email():
    admin = Usuario.objects.create_superuser(
        email="admin@example.com", password="Admin123!"
    )
    assert admin.is_superuser is True
    assert admin.rol == Usuario.ROL_ADMINISTRADOR
    assert admin.is_staff is True
    assert admin.acepta_datos_en is None
    assert Usuario.objects.filter(email="admin@example.com").exists()
