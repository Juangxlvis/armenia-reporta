from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .serializers import ReporteCreateSerializer


class ReporteCreateView(generics.CreateAPIView):
    serializer_class = ReporteCreateSerializer
    permission_classes = [IsAuthenticated]
