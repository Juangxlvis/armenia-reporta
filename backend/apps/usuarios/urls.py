from django.urls import path

from .views import (
    ConfirmarView,
    LoginView,
    LogoutView,
    PerfilView,
    RecuperarView,
    ReenviarView,
    RefreshView,
    RegistroView,
    RestablecerView,
)

urlpatterns = [
    path("registro/", RegistroView.as_view(), name="registro"),
    path("confirmar/", ConfirmarView.as_view(), name="confirmar"),
    path(
        "reenviar-confirmacion/",
        ReenviarView.as_view(),
        name="reenviar-confirmacion",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("recuperar/", RecuperarView.as_view(), name="recuperar"),
    path("restablecer/", RestablecerView.as_view(), name="restablecer"),
    path("perfil/", PerfilView.as_view(), name="perfil"),
]
