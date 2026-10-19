from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reportes.models import Reporte

from .models import Apoyo


class ApoyoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        reporte = get_object_or_404(Reporte, pk=pk)
        if reporte.usuario_id == request.user.id:
            return Response(
                {"detail": "No puedes apoyar tu propio reporte"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            _, creado = Apoyo.objects.get_or_create(
                reporte=reporte, usuario=request.user
            )
            if not creado:
                return Response(
                    {"detail": "Ya apoyaste este reporte"},
                    status=status.HTTP_409_CONFLICT,
                )
            Reporte.objects.filter(pk=reporte.pk).update(
                total_apoyos=F("total_apoyos") + 1
            )

        reporte.refresh_from_db()
        return Response(
            {"total_apoyos": reporte.total_apoyos}, status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        reporte = get_object_or_404(Reporte, pk=pk)
        with transaction.atomic():
            borrados, _ = Apoyo.objects.filter(
                reporte=reporte, usuario=request.user
            ).delete()
            if borrados == 0:
                return Response(
                    {"detail": "No has apoyado este reporte"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            Reporte.objects.filter(pk=reporte.pk).update(
                total_apoyos=F("total_apoyos") - 1
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
