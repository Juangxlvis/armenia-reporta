from rest_framework import serializers

from apps.reportes.models import Reporte


class ReporteAdminSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    estado_id = serializers.IntegerField(read_only=True)
    estado_nombre = serializers.CharField(source="estado.nombre", read_only=True)
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Reporte
        fields = [
            "id",
            "folio",
            "titulo",
            "categoria_nombre",
            "estado_id",
            "estado_nombre",
            "usuario_nombre",
            "creado_en",
        ]

    def get_usuario_nombre(self, obj):
        return obj.usuario.nombre or obj.usuario.email
