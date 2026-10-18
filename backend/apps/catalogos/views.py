from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Categoria
from .serializers import CategoriaSerializer


class CategoriaListView(generics.ListAPIView):
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Categoria.objects.filter(activa=True).order_by("nombre")
