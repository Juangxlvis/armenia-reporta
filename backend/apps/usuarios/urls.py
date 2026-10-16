from django.urls import path

from .views import ConfirmarView, ReenviarView, RegistroView

urlpatterns = [
    path("registro/", RegistroView.as_view(), name="registro"),
    path("confirmar/", ConfirmarView.as_view(), name="confirmar"),
    path(
        "reenviar-confirmacion/",
        ReenviarView.as_view(),
        name="reenviar-confirmacion",
    ),
]
