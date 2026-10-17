from django.core.management.base import BaseCommand

from apps.catalogos.models import Categoria
from apps.estados.models import Estado

CATEGORIAS = ["vías", "alumbrado", "residuos", "espacio público", "señalización"]

ESTADOS = [
    {"codigo": "reportado", "nombre": "Reportado", "orden": 1, "es_final": False},
    {"codigo": "en_revision", "nombre": "En revisión", "orden": 2, "es_final": False},
    {"codigo": "en_proceso", "nombre": "En proceso", "orden": 3, "es_final": False},
    {"codigo": "solucionado", "nombre": "Solucionado", "orden": 4, "es_final": True},
]


class Command(BaseCommand):
    help = "Siembra los catálogos iniciales: categorías y estados."

    def handle(self, *args, **options):
        categorias_creadas = 0
        categorias_existentes = 0
        for nombre in CATEGORIAS:
            _, creada = Categoria.objects.get_or_create(nombre=nombre)
            if creada:
                categorias_creadas += 1
            else:
                categorias_existentes += 1

        estados_creados = 0
        estados_existentes = 0
        for datos in ESTADOS:
            _, creado = Estado.objects.get_or_create(
                codigo=datos["codigo"],
                defaults={
                    "nombre": datos["nombre"],
                    "orden": datos["orden"],
                    "es_final": datos["es_final"],
                },
            )
            if creado:
                estados_creados += 1
            else:
                estados_existentes += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Categorías: {categorias_creadas} creadas, "
                f"{categorias_existentes} ya existían."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Estados: {estados_creados} creados, "
                f"{estados_existentes} ya existían."
            )
        )
