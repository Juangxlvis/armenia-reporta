from django.urls import path

from .views import CategoriaListView

urlpatterns = [
    path("", CategoriaListView.as_view(), name="listar-categorias"),
]
