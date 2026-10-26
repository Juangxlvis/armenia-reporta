from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Categoria, Zona
from .serializers import CategoriaSerializer, ZonaSerializer


class CategoriaListView(generics.ListAPIView):
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Categoria.objects.filter(activa=True).order_by("nombre")


class ZonaListView(generics.ListAPIView):
    serializer_class = ZonaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Zona.objects.filter(activa=True).order_by("nombre")
