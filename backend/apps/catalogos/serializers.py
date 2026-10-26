from rest_framework import serializers

from .models import Categoria, Zona


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre"]


class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = ["id", "nombre"]
