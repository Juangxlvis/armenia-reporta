from datetime import timedelta

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("activo", True)
        extra_fields.setdefault("correo_confirmado", True)
        extra_fields.setdefault("rol", Usuario.ROL_ADMINISTRADOR)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    ROL_CIUDADANO = "ciudadano"
    ROL_FUNCIONARIO = "funcionario"
    ROL_ADMINISTRADOR = "administrador"
    ROL_CHOICES = [
        (ROL_CIUDADANO, "Ciudadano"),
        (ROL_FUNCIONARIO, "Funcionario"),
        (ROL_ADMINISTRADOR, "Administrador"),
    ]

    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=150, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default=ROL_CIUDADANO)
    activo = models.BooleanField(default=False)
    correo_confirmado = models.BooleanField(default=False)
    intentos_fallidos = models.PositiveIntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)
    acepta_datos_en = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.email

    @property
    def is_active(self):
        return self.activo

    @property
    def is_staff(self):
        return self.is_superuser or self.rol == self.ROL_ADMINISTRADOR


class TokenUsuario(models.Model):
    TIPO_CONFIRMACION = "confirmacion"
    TIPO_RECUPERACION = "recuperacion"
    TIPO_CHOICES = [
        (TIPO_CONFIRMACION, "Confirmación"),
        (TIPO_RECUPERACION, "Recuperación"),
    ]

    VIGENCIA = {
        TIPO_CONFIRMACION: timedelta(hours=24),
        TIPO_RECUPERACION: timedelta(minutes=15),
    }

    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="tokens"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    token = models.CharField(max_length=64)
    expira_en = models.DateTimeField()
    usado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "token de usuario"
        verbose_name_plural = "tokens de usuario"

    def __str__(self):
        return f"{self.tipo} de {self.usuario.email}"
