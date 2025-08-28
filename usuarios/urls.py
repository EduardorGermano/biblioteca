# usuarios/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    CadastroUsuarioView, 
    UsuarioListView, 
    UsuarioUpdateView, 
    UsuarioDeleteView,
)

urlpatterns = [
    # URLs de autenticação
    path('', auth_views.LoginView.as_view(
        template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("registrar/", CadastroUsuarioView.as_view(), name="registrar"),
    
    # URLs de gerenciamento de usuários (apenas para administradores)
    path('usuarios/', UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/editar/<int:pk>/', UsuarioUpdateView.as_view(), name='usuario_update'),
    path('usuarios/excluir/<int:pk>/', UsuarioDeleteView.as_view(), name='usuario_delete'),
]