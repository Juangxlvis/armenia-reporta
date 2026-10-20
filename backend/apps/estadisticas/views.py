from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reportes.models import Reporte
from apps.usuarios.models import Usuario


class ResumenEstadisticasView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        estados_en_proceso = ["en_revision", "en_proceso"]
        return Response(
            {
                "total_reportes": Reporte.objects.count(),
                "en_proceso": Reporte.objects.filter(
                    estado__codigo__in=estados_en_proceso
                ).count(),
                "resueltos": Reporte.objects.filter(
                    estado__codigo="solucionado"
                ).count(),
                "ciudadanos": Usuario.objects.filter(rol=Usuario.ROL_CIUDADANO).count(),
            }
        )
