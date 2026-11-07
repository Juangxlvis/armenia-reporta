import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.catalogos.models import Categoria, Zona
from apps.estados.models import Estado

class Command(BaseCommand):
    help = 'Inicializa datos esenciales para producción (categorías, estados, zonas y superusuario)'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando inicialización de datos...")

        # 1. Crear Categorías
        categorias = ['vías', 'alumbrado', 'residuos', 'espacio público', 'señalización']
        for nombre in categorias:
            Categoria.objects.get_or_create(nombre=nombre)
        self.stdout.write(self.style.SUCCESS('✓ Categorías creadas/verificadas.'))

        # 2. Crear Estados
        estados = [
            {'codigo': 'reportado', 'nombre': 'Reportado', 'orden': 1},
            {'codigo': 'en_revision', 'nombre': 'En revisión', 'orden': 2},
            {'codigo': 'en_proceso', 'nombre': 'En proceso', 'orden': 3},
            {'codigo': 'solucionado', 'nombre': 'Solucionado', 'orden': 4, 'es_final': True},
        ]
        for data in estados:
            Estado.objects.get_or_create(codigo=data['codigo'], defaults=data)
        self.stdout.write(self.style.SUCCESS('✓ Estados creados/verificados.'))

        # 3. Crear Zonas (Comunas de Armenia)
        zonas = ['Centenario', 'Rufino José Cuervo', 'Alfonso López', 'Francisco de Paula Santander', 
                 'El Bosque', 'San José', 'Cafetero', 'Libertadores', 'Fundadores', 'Quimbaya']
        for nombre in zonas:
            Zona.objects.get_or_create(nombre=nombre)
        self.stdout.write(self.style.SUCCESS('✓ Zonas creadas/verificadas.'))

        # 4. Crear Superusuario desde variables de entorno
        User = get_user_model()
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        
        if email and password:
            if not User.objects.filter(email=email).exists():
                User.objects.create_superuser(email=email, nombre='Admin', password=password)
                self.stdout.write(self.style.SUCCESS(f'✓ Superusuario {email} creado.'))
            else:
                self.stdout.write(self.style.WARNING(f'El superusuario {email} ya existe.'))
        else:
            self.stdout.write(self.style.WARNING('⚠ No se configuraron las variables DJANGO_SUPERUSER_EMAIL y DJANGO_SUPERUSER_PASSWORD.'))
        
        self.stdout.write(self.style.SUCCESS('¡Inicialización completada!'))