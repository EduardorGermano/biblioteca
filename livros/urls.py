from django.urls import path

#CREATE
from .views import AutorCreateView, GeneroCreateView, LivroCreateView
#UPDATE
from .views import AutorUpdateView, GeneroUpdateView, LivroUpdateView
#DELETE
from .views import AutorDeleteView, GeneroDeleteView, LivroDeleteView
#LIST
from .views import AutorListView, GeneroListView, LivroListView, LivrosDisponiveisView
#EMPRESTIMO
from . import views


urlpatterns = [
   path('autor/novo/', AutorCreateView.as_view(), name='autor_create'),
   path('genero/novo/', GeneroCreateView.as_view(), name='genero_create'),
   path('novo/', LivroCreateView.as_view(), name='livro_create'),

   path('autor/editar/<int:pk>/', AutorUpdateView.as_view(), name='editar_autor'),
   path('genero/editar/<int:pk>/', GeneroUpdateView.as_view(), name='editar_genero'),
   path('editar/<int:pk>/', LivroUpdateView.as_view(), name='editar_livro'),

   path('autor/excluir/<int:pk>/', AutorDeleteView.as_view(), name='excluir_autor'),
   path('genero/excluir/<int:pk>/', GeneroDeleteView.as_view(), name='excluir_genero'),
   path('excluir/<int:pk>/', LivroDeleteView.as_view(), name='excluir_livro'),

   path('autor/lista/', AutorListView.as_view(), name='autor_list'),
   path('genero/lista/', GeneroListView.as_view(), name='genero_list'),
   path('lista/', LivroListView.as_view(), name='livro_list'),

   path('livros-disponiveis/', LivrosDisponiveisView.as_view(), name='livros_disponiveis'),
   path('emprestimo/<int:livro_id>/', views.realizar_emprestimo, name='realizar_emprestimo'),
   path('devolver/<int:emprestimo_id>/', views.devolver_livro, name='devolver_livro'),
   path('meus-emprestimos/', views.meus_emprestimos, name='meus_emprestimos'),

] 