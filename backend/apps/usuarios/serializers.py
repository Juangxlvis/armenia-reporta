from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import TokenUsuario, Usuario
from .services import _hash_token, crear_token, enviar_correo_confirmacion


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


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError as exc:
            raise serializers.ValidationError({"detail": "Token inválido"}) from exc


class ConfirmarSerializer(serializers.Serializer):
    token = serializers.CharField()


class ReenviarSerializer(serializers.Serializer):
    email = serializers.EmailField()


class RecuperarSerializer(serializers.Serializer):
    email = serializers.EmailField()


class RestablecerSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_token(self, value):
        token_hash = _hash_token(value)
        try:
            token_db = TokenUsuario.objects.get(
                token=token_hash, tipo=TokenUsuario.TIPO_RECUPERACION
            )
        except TokenUsuario.DoesNotExist:
            raise serializers.ValidationError("Token inválido")
        if token_db.usado_en is not None:
            raise serializers.ValidationError("El token ya fue usado")
        if token_db.expira_en < timezone.now():
            raise serializers.ValidationError("El token ha expirado")
        self.token_db = token_db
        return value

    def validate_password(self, value):
        token_db = getattr(self, "token_db", None)
        usuario = token_db.usuario if token_db is not None else None
        try:
            validate_password(value, user=usuario)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def save(self, **kwargs):
        usuario = self.token_db.usuario
        usuario.set_password(self.validated_data["password"])
        usuario.save()
        self.token_db.usado_en = timezone.now()
        self.token_db.save()
        return usuario
