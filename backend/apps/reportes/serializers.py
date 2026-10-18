from django.contrib.gis.geos import Point
from django.core.files.storage import default_storage
from rest_framework import serializers

from apps.catalogos.models import Categoria
from apps.estados.models import Estado

from .models import FotoReporte, Reporte
from .utils import comprimir_foto, validar_foto

DESCRIPCION_MINIMA = 20


class FotoReporteSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = FotoReporte
        fields = ["id", "clave_almacenamiento", "orden", "url"]
        read_only_fields = fields

    def get_url(self, obj):
        return default_storage.url(obj.clave_almacenamiento)


class ReporteCreateSerializer(serializers.ModelSerializer):
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.filter(activa=True)
    )
    lat = serializers.FloatField(write_only=True)
    lng = serializers.FloatField(write_only=True)
    fotos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        max_length=3,
    )

    class Meta:
        model = Reporte
        fields = [
            "id",
            "titulo",
            "descripcion",
            "categoria",
            "lat",
            "lng",
            "fotos",
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

    def validate_fotos(self, value):
        for foto in value:
            validar_foto(foto)
        return value

    def create(self, validated_data):
        fotos = validated_data.pop("fotos", [])
        lat = validated_data.pop("lat")
        lng = validated_data.pop("lng")
        validated_data["ubicacion"] = Point(lng, lat, srid=4326)
        validated_data["estado"] = Estado.objects.get(codigo="reportado")
        validated_data["usuario"] = self.context["request"].user
        reporte = super().create(validated_data)
        for orden, foto in enumerate(fotos):
            comprimida = comprimir_foto(foto)
            clave = default_storage.save(
                f"reportes/{reporte.id}/{comprimida.name}", comprimida
            )
            FotoReporte.objects.create(
                reporte=reporte, clave_almacenamiento=clave, orden=orden
            )
        return reporte

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["fotos"] = FotoReporteSerializer(
            instance.fotos.all(), many=True, context=self.context
        ).data
        return data
