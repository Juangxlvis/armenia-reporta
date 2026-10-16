from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import TokenUsuario, Usuario
from .serializers import (
    ConfirmarSerializer,
    LoginSerializer,
    LogoutSerializer,
    ReenviarSerializer,
    RegistroSerializer,
)
from .services import (
    ResultadoLogin,
    _hash_token,
    crear_token,
    enviar_correo_confirmacion,
    iniciar_sesion,
)

RESPUESTAS_LOGIN = {
    ResultadoLogin.BLOQUEADO: (
        "Cuenta bloqueada temporalmente por intentos fallidos",
        status.HTTP_403_FORBIDDEN,
    ),
    ResultadoLogin.CREDENCIALES_INVALIDAS: (
        "Credenciales inválidas",
        status.HTTP_401_UNAUTHORIZED,
    ),
    ResultadoLogin.NO_CONFIRMADO: (
        "El correo no está confirmado",
        status.HTTP_403_FORBIDDEN,
    ),
    ResultadoLogin.INACTIVO: (
        "La cuenta está inactiva",
        status.HTTP_403_FORBIDDEN,
    ),
}


class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resultado, usuario = iniciar_sesion(
            serializer.validated_data["email"],
            serializer.validated_data["password"],
        )

        if resultado is not ResultadoLogin.EXITO:
            detalle, codigo = RESPUESTAS_LOGIN[resultado]
            return Response({"detail": detalle}, status=codigo)

        refresh = RefreshToken.for_user(usuario)
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)})


class RefreshView(TokenRefreshView):
    pass


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Sesión cerrada"})


class PerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user
        return Response({"email": usuario.email, "nombre": usuario.nombre})


class ConfirmarView(APIView):
    def post(self, request):
        serializer = ConfirmarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_plano = serializer.validated_data["token"]
        token_hash = _hash_token(token_plano)
        try:
            token_db = TokenUsuario.objects.get(
                token=token_hash, tipo=TokenUsuario.TIPO_CONFIRMACION
            )
        except TokenUsuario.DoesNotExist:
            raise ValidationError({"detail": "Token inválido"})
        if token_db.usado_en is not None:
            raise ValidationError({"detail": "El token ya fue usado"})
        if token_db.expira_en < timezone.now():
            raise ValidationError({"detail": "El token ha expirado"})

        usuario = token_db.usuario
        usuario.correo_confirmado = True
        usuario.activo = True
        usuario.save()

        token_db.usado_en = timezone.now()
        token_db.save()

        return Response({"detail": "Cuenta confirmada"})


class ReenviarView(APIView):
    def post(self, request):
        serializer = ReenviarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        usuario = Usuario.objects.filter(email__iexact=email).first()

        if usuario is None:
            return Response(
                {"detail": "Si el correo está registrado, recibirás un enlace"}
            )
        if usuario.correo_confirmado:
            raise ValidationError({"detail": "El correo ya está confirmado"})

        token = crear_token(usuario, TokenUsuario.TIPO_CONFIRMACION)
        enviar_correo_confirmacion(usuario, token)
        return Response({"detail": "Se envió un nuevo enlace de confirmación"})
