from django.contrib.gis.geos import Point
from rest_framework import serializers

from apps.catalogos.models import Categoria
from apps.estados.models import Estado

from .models import Reporte

DESCRIPCION_MINIMA = 20


class ReporteCreateSerializer(serializers.ModelSerializer):
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.filter(activa=True)
    )
    lat = serializers.FloatField(write_only=True)
    lng = serializers.FloatField(write_only=True)

    class Meta:
        model = Reporte
        fields = [
            "id",
            "titulo",
            "descripcion",
            "categoria",
            "lat",
            "lng",
            "usuario",
            "estado",
            "total_apoyos",
            "creado_en",
        ]
        read_only_fields = [
            "id",
            "usuario",
            "estado",
            "total_apoyos",
            "creado_en",
        ]

    def validate_descripcion(self, value):
        if len(value.strip()) < DESCRIPCION_MINIMA:
            raise serializers.ValidationError(
                f"La descripción debe tener mínimo {DESCRIPCION_MINIMA} caracteres"
            )
        return value

    def create(self, validated_data):
        lat = validated_data.pop("lat")
        lng = validated_data.pop("lng")
        validated_data["ubicacion"] = Point(lng, lat, srid=4326)
        validated_data["estado"] = Estado.objects.get(codigo="reportado")
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)
