from django.contrib.gis.geos import Polygon
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from apps.reportes.models import Reporte
from apps.reportes.serializers import ReporteMapaSerializer


class ReportesMapaView(generics.ListAPIView):
    serializer_class = ReporteMapaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Reporte.objects.select_related("categoria", "estado").prefetch_related(
            "fotos"
        )
        categoria = self.request.query_params.get("categoria")
        estado = self.request.query_params.get("estado")
        bbox = self.request.query_params.get("bbox")

        if categoria:
            qs = qs.filter(categoria_id=categoria)
        if estado:
            qs = qs.filter(estado_id=estado)
        if bbox:
            qs = qs.filter(ubicacion__bboverlaps=self._poligono_bbox(bbox))
        return qs[:500]

    @staticmethod
    def _poligono_bbox(bbox):
        try:
            partes = [float(valor) for valor in bbox.split(",")]
        except (TypeError, ValueError) as exc:
            raise ValidationError({"bbox": "formato inválido"}) from exc
        if len(partes) != 4:
            raise ValidationError({"bbox": "formato inválido"})
        return Polygon.from_bbox(partes)
