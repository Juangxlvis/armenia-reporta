from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.estados.models import Estado
from apps.reportes.models import Reporte
from apps.usuarios.permissions import IsFuncionarioOrAdmin

from .serializers import ReporteAdminSerializer


def _parametro_entero(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


class ReporteAdminListView(generics.ListAPIView):
    serializer_class = ReporteAdminSerializer
    permission_classes = [IsFuncionarioOrAdmin]

    def get_queryset(self):
        queryset = Reporte.objects.select_related(
            "categoria", "estado", "usuario", "zona"
        ).order_by("-creado_en")

        search = (self.request.query_params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(
                Q(folio__icontains=search)
                | Q(titulo__icontains=search)
                | Q(descripcion__icontains=search)
            )

        estado = _parametro_entero(self.request.query_params.get("estado"))
        if estado:
            queryset = queryset.filter(estado_id=estado)

        categoria = _parametro_entero(self.request.query_params.get("categoria"))
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)

        zona = _parametro_entero(self.request.query_params.get("zona"))
        if zona:
            queryset = queryset.filter(zona_id=zona)

        return queryset


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
