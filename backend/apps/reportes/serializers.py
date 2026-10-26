from django.contrib.gis.geos import Point
from django.core.files.storage import default_storage
from rest_framework import serializers

from apps.catalogos.models import Categoria, Zona
from apps.catalogos.serializers import CategoriaSerializer
from apps.estados.models import Estado, HistorialEstado

from .models import FotoReporte, Reporte
from .services import generar_folio
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
    zona_id = serializers.PrimaryKeyRelatedField(
        queryset=Zona.objects.filter(activa=True),
        source="zona",
        required=False,
        allow_null=True,
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
            "folio",
            "titulo",
            "descripcion",
            "categoria",
            "zona_id",
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
            "folio",
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
        validated_data["folio"] = generar_folio()
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


class ReporteResumenSerializer(serializers.ModelSerializer):
    resumen = serializers.SerializerMethodField()
    categoria_id = serializers.IntegerField(read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    estado_id = serializers.IntegerField(read_only=True)
    estado_nombre = serializers.CharField(source="estado.nombre", read_only=True)
    primera_foto = serializers.SerializerMethodField()

    class Meta:
        model = Reporte
        fields = [
            "id",
            "folio",
            "titulo",
            "resumen",
            "categoria_id",
            "categoria_nombre",
            "estado_id",
            "estado_nombre",
            "total_apoyos",
            "creado_en",
            "primera_foto",
        ]

    def get_resumen(self, obj):
        return obj.descripcion[:100]

    def get_primera_foto(self, obj):
        foto = obj.fotos.first()
        if foto is None:
            return None
        return {
            "url": default_storage.url(foto.clave_almacenamiento),
            "clave_almacenamiento": foto.clave_almacenamiento,
        }


class UbicacionSerializerMixin:
    def get_lat(self, obj):
        return obj.ubicacion.y

    def get_lng(self, obj):
        return obj.ubicacion.x


class ReporteMapaSerializer(UbicacionSerializerMixin, ReporteResumenSerializer):
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()

    class Meta(ReporteResumenSerializer.Meta):
        fields = ReporteResumenSerializer.Meta.fields + ["lat", "lng"]


class EstadoResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ["id", "nombre"]


class ReporteDetalleSerializer(UbicacionSerializerMixin, serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    estado = EstadoResumenSerializer(read_only=True)
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()
    fotos = FotoReporteSerializer(many=True, read_only=True)
    usuario_nombre = serializers.SerializerMethodField()
    apoyado_por_mi = serializers.SerializerMethodField()

    class Meta:
        model = Reporte
        fields = [
            "id",
            "folio",
            "titulo",
            "descripcion",
            "categoria",
            "estado",
            "lat",
            "lng",
            "total_apoyos",
            "creado_en",
            "resuelto_en",
            "fotos",
            "usuario_nombre",
            "apoyado_por_mi",
        ]

    def get_usuario_nombre(self, obj):
        nombre = obj.usuario.nombre or ""
        return nombre.split()[0] if nombre.strip() else ""

    def get_apoyado_por_mi(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return obj.apoyos.filter(usuario=request.user).exists()


class HistorialEstadoSerializer(serializers.ModelSerializer):
    estado_anterior_nombre = serializers.SerializerMethodField()
    estado_nuevo_nombre = serializers.SerializerMethodField()

    class Meta:
        model = HistorialEstado
        fields = [
            "estado_anterior_nombre",
            "estado_nuevo_nombre",
            "comentario",
            "cambiado_en",
        ]

    def get_estado_anterior_nombre(self, obj):
        return obj.estado_anterior.nombre if obj.estado_anterior else None

    def get_estado_nuevo_nombre(self, obj):
        return obj.estado_nuevo.nombre if obj.estado_nuevo else None
