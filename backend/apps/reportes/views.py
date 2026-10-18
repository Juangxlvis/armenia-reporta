from rest_framework import generics, parsers
from rest_framework.permissions import IsAuthenticated

from .serializers import ReporteCreateSerializer
from .services import enviar_correo_confirmacion_reporte


class ReporteCreateView(generics.CreateAPIView):
    serializer_class = ReporteCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def perform_create(self, serializer):
        reporte = serializer.save()
        enviar_correo_confirmacion_reporte(self.request.user, reporte)
