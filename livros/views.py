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
from .forms import LivroForm
from django import forms
from django.db import transaction

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
    
    extra_context = {
        "btn_cadastro": "Cadastrar Autor",
    }

class GeneroCreateView(AdminRequiredMixin, CreateView):
    model = Genero
    template_name = 'formularios/formulario.html'
    fields = ['nome']
    success_url = reverse_lazy('genero_list')
    
    extra_context = {
        "btn_cadastro" : "Cadastrar Genero",
    }
    

class LivroCreateView(AdminRequiredMixin, CreateView):
    model = Livro
    template_name = 'formularios/formulario.html'
    form_class = LivroForm
    success_url = reverse_lazy('livro_list')
    
    extra_context = {
        "btn_cadastro" : "Cadastrar Livro",
    }


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
    form_class = LivroForm
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
    paginate_by = 20

    def get_queryset(self):
        # Otimização: quando listando livros, traga autor e genero para evitar N+1
        return Livro.objects.select_related('autor', 'genero').all()


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
    # Otimização: trazer o livro relacionado para evitar consultas extras no template
    emprestimos = Emprestimo.objects.filter(usuario=request.user).select_related('livro').order_by('-data_emprestimo')
    return render(request, 'meus_emprestimos.html', {'emprestimos': emprestimos})

class LivrosDisponiveisView(LoginRequiredMixin, ListView):
    model = Livro
    template_name = 'livros_disponiveis.html'
    context_object_name = 'livros'
    paginate_by = 12
    def get_queryset(self):
        # Base: apenas livros disponíveis
        qs = Livro.objects.filter(disponivel=True)

        # Filtros via querystring
        q = self.request.GET.get('q')
        autor = self.request.GET.get('autor')
        genero = self.request.GET.get('genero')
        estado = self.request.GET.get('estado')

        if q:
            qs = qs.filter(titulo__icontains=q)

        if autor:
            try:
                qs = qs.filter(autor_id=int(autor))
            except (ValueError, TypeError):
                pass

        if genero:
            try:
                qs = qs.filter(genero_id=int(genero))
            except (ValueError, TypeError):
                pass

        if estado:
            qs = qs.filter(estado=estado)

        # Otimização: trazer autor e genero para evitar consultas N+1 na listagem
        qs = qs.select_related('autor', 'genero')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Listas para os selects do formulário de filtro
        context['autores'] = Autor.objects.all()
        context['generos'] = Genero.objects.all()
        # Estados a partir das choices do modelo
        context['estados'] = [c[0] for c in Livro._meta.get_field('estado').choices]
        # Querystring atual sem o parâmetro page — útil para manter filtros ao paginar
        qs = self.request.GET.copy()
        if 'page' in qs:
            qs.pop('page')
        context['querystring'] = qs.urlencode()
        return context


class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = []  # nenhum campo exposto; serão preenchidos em form_valid


class EmprestimoCreateView(LoginRequiredMixin, CreateView):
    model = Emprestimo
    form_class = EmprestimoForm
    # não usamos template específico aqui porque o formulário simples é apenas um botão

    def dispatch(self, request, *args, **kwargs):
        # carregar o livro a partir da URL
        self.livro = get_object_or_404(Livro, id=kwargs.get('livro_id'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Para evitar condição de corrida, usamos uma transação e lock no registro do livro
        try:
            with transaction.atomic():
                livro = Livro.objects.select_for_update().get(pk=self.livro.pk)
                if not livro.disponivel:
                    form.add_error(None, 'Este livro não está disponível para empréstimo.')
                    return self.form_invalid(form)

                emprestimo = form.save(commit=False)
                emprestimo.livro = livro
                emprestimo.usuario = self.request.user
                emprestimo.data_devolucao_prevista = timezone.now() + timedelta(days=14)

                # validação do modelo
                try:
                    emprestimo.full_clean()
                except ValidationError as e:
                    form.add_error(None, e)
                    return self.form_invalid(form)

                emprestimo.save()

                # atualiza disponibilidade do livro
                livro.disponivel = False
                livro.save()

        except Livro.DoesNotExist:
            form.add_error(None, 'Livro não encontrado.')
            return self.form_invalid(form)

        messages.success(self.request, 'Empréstimo realizado com sucesso!')
        return redirect('meus_emprestimos')

    def form_invalid(self, form):
        # Em vez de renderizar um template de formulário (que não existe aqui),
        # redirecionamos com mensagem de erro para a lista de livros disponíveis.
        errors = form.non_field_errors()
        if errors:
            for e in errors:
                messages.error(self.request, str(e))
        else:
            messages.error(self.request, 'Erro ao processar o empréstimo.')
        return redirect('livros_disponiveis')
    

