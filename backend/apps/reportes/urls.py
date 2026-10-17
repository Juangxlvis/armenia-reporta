from django.urls import path

from .views import ReporteCreateView

urlpatterns = [
    path("", ReporteCreateView.as_view(), name="crear-reporte"),
]
