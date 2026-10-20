from django.contrib.gis.db import models
from django.utils import timezone

from apps.catalogos.models import Categoria
from apps.estados.models import Estado
from apps.usuarios.models import Usuario


class Reporte(models.Model):
    folio = models.CharField(max_length=30, unique=True)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="reportes"
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="reportes"
    )
    estado = models.ForeignKey(
        Estado, on_delete=models.PROTECT, related_name="reportes"
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    ubicacion = models.PointField(srid=4326, spatial_index=True)
    total_apoyos = models.PositiveIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    resuelto_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "reporte"
        verbose_name_plural = "reportes"
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["categoria"]),
            models.Index(fields=["creado_en"]),
        ]

    def __str__(self):
        return self.titulo

    def crear_historial_inicial(self):
        from apps.estados.models import HistorialEstado

        HistorialEstado.objects.create(
            reporte=self,
            estado_anterior=None,
            estado_nuevo=self.estado,
            cambiado_por=self.usuario,
        )

    def avanzar_estado(self, nuevo_estado, cambiado_por, comentario):
        from apps.estados.models import HistorialEstado

        if nuevo_estado.orden != self.estado.orden + 1:
            raise ValueError("Solo se permite avanzar al siguiente estado")

        estado_anterior = self.estado
        self.estado = nuevo_estado
        if nuevo_estado.es_final:
            self.resuelto_en = timezone.now()
        self.save(update_fields=["estado", "resuelto_en", "actualizado_en"])

        HistorialEstado.objects.create(
            reporte=self,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            cambiado_por=cambiado_por,
            comentario=comentario,
        )


class FotoReporte(models.Model):
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name="fotos")
    clave_almacenamiento = models.CharField(max_length=255)
    orden = models.PositiveSmallIntegerField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "foto de reporte"
        verbose_name_plural = "fotos de reporte"
        ordering = ["orden"]

    def __str__(self):
        return f"{self.reporte_id}-{self.orden}"
