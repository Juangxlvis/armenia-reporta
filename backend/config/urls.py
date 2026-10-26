from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.catalogos.views import ZonaListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.usuarios.urls")),
    path("api/reportes/", include("apps.reportes.urls")),
    path("api/reportes/", include("apps.apoyos.urls")),
    path("api/categorias/", include("apps.catalogos.urls")),
    path("api/zonas/", ZonaListView.as_view(), name="listar-zonas"),
    path("api/mapa/", include("apps.mapa.urls")),
    path("api/admin/", include("apps.administracion.urls")),
    path("api/estadisticas/", include("apps.estadisticas.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
