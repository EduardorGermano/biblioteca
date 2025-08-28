from datetime import timedelta
from django.forms import ValidationError
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Emprestimo, Livro
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required  
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from livros.models import Autor, Genero, Livro

# Defina a mixin primeiro, antes de usá-la nas views
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, "Acesso negado. Você não tem permissão de administrador.")
        return redirect('pagina_index')  # Altere para o nome da sua URL inicial

# Create your views here.

##### CREATE VIEW #####
class AutorCreateView(AdminRequiredMixin, CreateView):
    model = Autor
    template_name = 'formularios/formulario.html'
    fields = ['nome']
    success_url = reverse_lazy('autor_list')

class GeneroCreateView(AdminRequiredMixin, CreateView):
    model = Genero
    template_name = 'formularios/formulario.html'
    fields = ['nome']
    success_url = reverse_lazy('genero_list')

class LivroCreateView(AdminRequiredMixin, CreateView):
    model = Livro
    template_name = 'formularios/formulario.html'
    fields = ['titulo', 'autor', 'genero', 'disponivel', 'estado']
    success_url = reverse_lazy('livro_list')


##### UPDATE VIEW #####
class AutorUpdateView(AdminRequiredMixin, UpdateView):
    model = Autor
    template_name = 'formularios/formulario.html'
    fields = ['nome']
    success_url = reverse_lazy('autor_list')

class GeneroUpdateView(AdminRequiredMixin, UpdateView):
    model = Genero
    template_name = 'formularios/formulario.html'
    fields = ['nome']
    success_url = reverse_lazy('genero_list')


class LivroUpdateView(AdminRequiredMixin, UpdateView):
    model = Livro
    template_name = 'formularios/formulario.html'
    fields = ['titulo', 'autor', 'genero', 'disponivel', 'estado']
    success_url = reverse_lazy('livro_list')

##### DELETE VIEW #####
class AutorDeleteView(AdminRequiredMixin, DeleteView):
    model = Autor
    template_name = 'formularios/formulario_exclusao.html'
    fields = ['nome']
    success_url = reverse_lazy('autor_list')

class GeneroDeleteView(AdminRequiredMixin, DeleteView):
    model = Genero
    template_name = 'formularios/formulario_exclusao.html'
    fields = ['nome']
    success_url = reverse_lazy('genero_list')

class LivroDeleteView(AdminRequiredMixin, DeleteView):
    model = Livro
    template_name = 'formularios/formulario_exclusao.html'
    fields = ['titulo', 'autor', 'genero', 'disponivel', 'estado']
    success_url = reverse_lazy('livro_list')


##### LIST VIEW #####
class AutorListView(AdminRequiredMixin, ListView):
    model = Autor
    template_name = 'autor_list.html'
    context_object_name = 'autores'


class GeneroListView(AdminRequiredMixin, ListView):
    model = Genero
    template_name = 'genero_list.html'
    context_object_name = 'generos'


class LivroListView(AdminRequiredMixin, ListView):
    model = Livro
    template_name = 'livro_list.html'
    context_object_name = 'livros'


#### Gerenciar Emprestimo ####
@login_required
def realizar_emprestimo(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    
    if request.method == 'POST':
        try:
            emprestimo = Emprestimo(
                livro=livro,
                usuario=request.user,
                data_devolucao_prevista=timezone.now() + timedelta(days=14)
            )
            emprestimo.full_clean()  # Valida o empréstimo
            emprestimo.save()
            messages.success(request, f'Empréstimo realizado com sucesso!')
        except ValidationError as e:
            messages.error(request, f'Erro: {e}')

    return redirect('meus_emprestimos')

@login_required
def devolver_livro(request, emprestimo_id):
    emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id, usuario=request.user)
    
    if emprestimo.status == 'ativo':
        emprestimo.devolver()
        messages.success(request, f'Livro "{emprestimo.livro.titulo}" devolvido com sucesso!')
    else:
        messages.warning(request, 'Este empréstimo já foi finalizado.')
    
    return redirect('meus_emprestimos')

@login_required
def meus_emprestimos(request):
    emprestimos = Emprestimo.objects.filter(usuario=request.user).order_by('-data_emprestimo')
    return render(request, 'meus_emprestimos.html', {'emprestimos': emprestimos})

class LivrosDisponiveisView(LoginRequiredMixin, ListView):
    model = Livro
    template_name = 'livros_disponiveis.html'
    context_object_name = 'livros'

    def get_queryset(self):
        return Livro.objects.filter(disponivel=True)
    

