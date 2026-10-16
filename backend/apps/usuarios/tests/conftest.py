import pytest
from django.core import mail


@pytest.fixture(autouse=True)
def configurar_correo_locmem(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    mail.outbox.clear()
