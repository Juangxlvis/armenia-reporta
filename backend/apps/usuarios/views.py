from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TokenUsuario, Usuario
from .serializers import ConfirmarSerializer, ReenviarSerializer, RegistroSerializer
from .services import _hash_token, crear_token, enviar_correo_confirmacion


class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer


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
