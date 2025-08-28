from django.urls import path
from .views import PaginaView

urlpatterns = [
    path('pagina_inicial/', PaginaView.as_view(), name='pagina_index'),
]