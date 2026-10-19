from django.urls import path

from .views import ReportesMapaView

urlpatterns = [
    path("reportes/", ReportesMapaView.as_view(), name="reportes-mapa"),
]
