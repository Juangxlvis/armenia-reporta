from django.conf import settings
from django.utils.module_loading import import_string
from storages.backends.s3 import S3Storage

APPS_ESPERADAS = {
    "apps.usuarios",
    "apps.reportes",
    "apps.apoyos",
    "apps.estados",
    "apps.mapa",
    "apps.estadisticas",
    "apps.administracion",
    "apps.catalogos",
}


def test_apps_de_dominio_instaladas():
    assert APPS_ESPERADAS.issubset(set(settings.INSTALLED_APPS))


def test_drf_y_simplejwt_instalados():
    assert "rest_framework" in settings.INSTALLED_APPS
    assert "rest_framework_simplejwt" in settings.INSTALLED_APPS


def test_jwt_configurado():
    assert settings.SIMPLE_JWT["AUTH_HEADER_TYPES"] == ("Bearer",)
    assert settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds() > 0


def test_storages_default_usa_s3():
    default = settings.STORAGES["default"]
    assert import_string(default["BACKEND"]) is S3Storage
    assert default["OPTIONS"]["region_name"] == "auto"
    assert default["OPTIONS"]["querystring_auth"] is False
    assert default["OPTIONS"]["file_overwrite"] is False
    assert settings.STORAGES["staticfiles"]["BACKEND"] == (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )
