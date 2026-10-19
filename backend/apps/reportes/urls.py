from django.urls import path

from .views import (
    HistorialReporteView,
    MisReportesView,
    ReporteCreateView,
    ReporteDetalleView,
)

urlpatterns = [
    path("", ReporteCreateView.as_view(), name="crear-reporte"),
    path("mios/", MisReportesView.as_view(), name="mis-reportes"),
    path("<int:pk>/", ReporteDetalleView.as_view(), name="detalle-reporte"),
    path(
        "<int:pk>/historial/",
        HistorialReporteView.as_view(),
        name="historial-reporte",
    ),
]
