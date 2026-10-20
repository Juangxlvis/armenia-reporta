from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.estados.models import Estado
from apps.reportes.models import Reporte
from apps.usuarios.permissions import IsFuncionarioOrAdmin

from .serializers import ReporteAdminSerializer


class ReporteAdminListView(generics.ListAPIView):
    serializer_class = ReporteAdminSerializer
    permission_classes = [IsFuncionarioOrAdmin]

    def get_queryset(self):
        return Reporte.objects.select_related(
            "categoria", "estado", "usuario"
        ).order_by("-creado_en")


class ReporteCambiarEstadoView(APIView):
    permission_classes = [IsFuncionarioOrAdmin]

    def patch(self, request, pk):
        reporte = get_object_or_404(
            Reporte.objects.select_related("categoria", "estado", "usuario"), pk=pk
        )
        estado_id = request.data.get("estado_id")
        comentario = request.data.get("comentario")

        if not comentario or not str(comentario).strip():
            raise ValidationError({"comentario": "La justificación es obligatoria"})

        try:
            nuevo_estado = Estado.objects.get(pk=estado_id)
        except (Estado.DoesNotExist, ValueError, TypeError) as exc:
            raise ValidationError({"estado_id": "Estado inválido"}) from exc

        try:
            with transaction.atomic():
                reporte.avanzar_estado(nuevo_estado, request.user, comentario)
        except ValueError as exc:
            raise ValidationError({"estado_id": str(exc)}) from exc

        reporte.refresh_from_db()
        return Response(ReporteAdminSerializer(reporte).data, status=status.HTTP_200_OK)
