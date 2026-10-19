from django.db import models


class Estado(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    orden = models.IntegerField()
    es_final = models.BooleanField(default=False)

    class Meta:
        verbose_name = "estado"
        verbose_name_plural = "estados"

    def __str__(self):
        return self.nombre


class HistorialEstado(models.Model):
    reporte = models.ForeignKey(
        "reportes.Reporte", on_delete=models.CASCADE, related_name="historial"
    )
    estado_anterior = models.ForeignKey(
        Estado, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    estado_nuevo = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name="+")
    cambiado_por = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    comentario = models.TextField(blank=True)
    cambiado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "historial de estado"
        verbose_name_plural = "historial de estados"
        indexes = [
            models.Index(fields=["reporte", "cambiado_en"]),
        ]

    def __str__(self):
        return f"{self.reporte_id} -> {self.estado_nuevo_id}"
