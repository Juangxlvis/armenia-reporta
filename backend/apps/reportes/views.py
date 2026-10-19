from rest_framework import generics, parsers
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.estados.models import HistorialEstado

from .models import Reporte
from .serializers import (
    HistorialEstadoSerializer,
    ReporteCreateSerializer,
    ReporteDetalleSerializer,
    ReporteResumenSerializer,
)
from .services import enviar_correo_confirmacion_reporte


class ReporteCreateView(generics.CreateAPIView):
    serializer_class = ReporteCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def perform_create(self, serializer):
        reporte = serializer.save()
        reporte.crear_historial_inicial()
        enviar_correo_confirmacion_reporte(self.request.user, reporte)


class MisReportesView(generics.ListAPIView):
    serializer_class = ReporteResumenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Reporte.objects.filter(usuario=self.request.user)
            .select_related("categoria", "estado")
            .prefetch_related("fotos")
            .order_by("-creado_en")
        )


class ReporteDetalleView(generics.RetrieveAPIView):
    serializer_class = ReporteDetalleSerializer
    permission_classes = [AllowAny]
    queryset = Reporte.objects.select_related(
        "categoria", "estado", "usuario"
    ).prefetch_related("fotos")


class HistorialReporteView(generics.ListAPIView):
    serializer_class = HistorialEstadoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            HistorialEstado.objects.filter(reporte_id=self.kwargs["pk"])
            .select_related("estado_anterior", "estado_nuevo")
            .order_by("cambiado_en")
        )
