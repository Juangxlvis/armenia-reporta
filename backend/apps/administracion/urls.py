from django.urls import path

from .views import ReporteAdminListView, ReporteCambiarEstadoView

urlpatterns = [
    path("reportes/", ReporteAdminListView.as_view(), name="admin-reportes"),
    path(
        "reportes/<int:pk>/estado/",
        ReporteCambiarEstadoView.as_view(),
        name="admin-reporte-estado",
    ),
]
