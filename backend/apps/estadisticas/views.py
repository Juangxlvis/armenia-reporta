from django.db.models import Count
from django.utils.dateparse import parse_date
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reportes.models import Reporte
from apps.usuarios.models import Usuario


def _filtrar_por_fecha(queryset, request):
    desde = parse_date(request.query_params.get("desde") or "")
    hasta = parse_date(request.query_params.get("hasta") or "")

    if desde:
        queryset = queryset.filter(creado_en__date__gte=desde)
    if hasta:
        queryset = queryset.filter(creado_en__date__lte=hasta)

    return queryset


class ResumenEstadisticasView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        estados_en_proceso = ["en_revision", "en_proceso"]
        reportes = _filtrar_por_fecha(Reporte.objects.all(), request)
        return Response(
            {
                "total_reportes": reportes.count(),
                "en_proceso": reportes.filter(
                    estado__codigo__in=estados_en_proceso
                ).count(),
                "resueltos": reportes.filter(estado__codigo="solucionado").count(),
                "ciudadanos": Usuario.objects.filter(rol=Usuario.ROL_CIUDADANO).count(),
            }
        )


class PorCategoriaEstadisticasView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        conteos = (
            _filtrar_por_fecha(Reporte.objects.all(), request)
            .values("categoria__nombre")
            .annotate(total=Count("id"))
            .order_by("-total", "categoria__nombre")
        )
        return Response(
            [
                {"categoria_nombre": item["categoria__nombre"], "total": item["total"]}
                for item in conteos
            ]
        )


class TiemposResolucionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        reportes = _filtrar_por_fecha(
            Reporte.objects.filter(
                estado__codigo="solucionado", resuelto_en__isnull=False
            ),
            request,
        ).select_related("categoria")

        duraciones: dict[str, list[float]] = {}
        for reporte in reportes:
            dias = (reporte.resuelto_en - reporte.creado_en).total_seconds() / 86400
            duraciones.setdefault(reporte.categoria.nombre, []).append(dias)

        return Response(
            [
                {
                    "categoria_nombre": nombre,
                    "promedio_dias": round(sum(valores) / len(valores), 1),
                }
                for nombre, valores in sorted(duraciones.items())
            ]
        )


class ZonasEstadisticasView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        conteos = (
            _filtrar_por_fecha(Reporte.objects.filter(zona__isnull=False), request)
            .values("zona__nombre")
            .annotate(total=Count("id"))
            .order_by("-total", "zona__nombre")
        )
        return Response(
            [
                {
                    "zona_nombre": item["zona__nombre"],
                    "total_reportes": item["total"],
                }
                for item in conteos
            ]
        )
