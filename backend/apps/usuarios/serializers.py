from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from .models import TokenUsuario, Usuario
from .services import crear_token, enviar_correo_confirmacion


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    acepta_datos = serializers.BooleanField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["email", "nombre", "telefono", "password", "acepta_datos"]

    def validate_email(self, value):
        if Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este correo")
        return value

    def validate_password(self, value):
        usuario = Usuario(
            email=self.initial_data.get("email", ""),
            nombre=self.initial_data.get("nombre", ""),
        )
        try:
            validate_password(value, user=usuario)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def validate_acepta_datos(self, value):
        if not value:
            raise serializers.ValidationError(
                "Debes aceptar la política de tratamiento de datos"
            )
        return value

    def create(self, validated_data):
        validated_data.pop("acepta_datos")
        password = validated_data.pop("password")
        usuario = Usuario.objects.create_user(
            password=password,
            activo=False,
            correo_confirmado=False,
            acepta_datos_en=timezone.now(),
            **validated_data,
        )
        token = crear_token(usuario, TokenUsuario.TIPO_CONFIRMACION)
        enviar_correo_confirmacion(usuario, token)
        return usuario


class ConfirmarSerializer(serializers.Serializer):
    token = serializers.CharField()


class ReenviarSerializer(serializers.Serializer):
    email = serializers.EmailField()
