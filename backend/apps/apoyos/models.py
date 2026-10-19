from django.db import models


class Apoyo(models.Model):
    reporte = models.ForeignKey(
        "reportes.Reporte", on_delete=models.CASCADE, related_name="apoyos"
    )
    usuario = models.ForeignKey(
        "usuarios.Usuario", on_delete=models.CASCADE, related_name="apoyos"
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "apoyo"
        verbose_name_plural = "apoyos"
        constraints = [
            models.UniqueConstraint(
                fields=["reporte", "usuario"], name="unique_apoyo_reporte_usuario"
            )
        ]

    def __str__(self):
        return f"Apoyo de {self.usuario_id} a {self.reporte_id}"
