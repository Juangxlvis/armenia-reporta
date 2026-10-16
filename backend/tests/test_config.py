from django.conf import settings

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
