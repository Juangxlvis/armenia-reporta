from django.urls import path

from .views import (
    PorCategoriaEstadisticasView,
    ResumenEstadisticasView,
    TiemposResolucionView,
    ZonasEstadisticasView,
)

urlpatterns = [
    path("resumen/", ResumenEstadisticasView.as_view(), name="estadisticas-resumen"),
    path(
        "por-categoria/",
        PorCategoriaEstadisticasView.as_view(),
        name="estadisticas-por-categoria",
    ),
    path("tiempos/", TiemposResolucionView.as_view(), name="estadisticas-tiempos"),
    path("zonas/", ZonasEstadisticasView.as_view(), name="estadisticas-zonas"),
]
