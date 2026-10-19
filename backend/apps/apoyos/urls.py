from django.urls import path

from .views import ApoyoView

urlpatterns = [
    path("<int:pk>/apoyos/", ApoyoView.as_view(), name="apoyar-reporte"),
]
