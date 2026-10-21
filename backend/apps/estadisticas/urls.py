from django.urls import path

from .views import PorCategoriaEstadisticasView, ResumenEstadisticasView

urlpatterns = [
    path("resumen/", ResumenEstadisticasView.as_view(), name="estadisticas-resumen"),
    path(
        "por-categoria/",
        PorCategoriaEstadisticasView.as_view(),
        name="estadisticas-por-categoria",
    ),
]
