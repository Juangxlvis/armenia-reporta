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
