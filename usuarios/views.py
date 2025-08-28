from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from .forms import UsuarioCadastroForm, UsuarioEdicaoForm

class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin que requer que o usuário seja administrador"""
    
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_superuser or 
            self.request.user.groups.filter(name='administrador').exists()
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'Acesso negado. Você precisa ser administrador.')
        return redirect('login')

class CadastroUsuarioView(CreateView):
    model = User
    form_class = UsuarioCadastroForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)

        # Adiciona ao grupo usuario
        grupo, criado = Group.objects.get_or_create(name='usuario')
        self.object.groups.add(grupo)
        
        # Define que o usuário está ativo
        self.object.is_active = True
        self.object.save()
        
        messages.success(
            self.request,
            'Conta criada com sucesso! Agora você pode fazer login.'
        )
        
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Por favor, corrija os erros abaixo.'
        )
        return super().form_invalid(form)

##### UPDATE VIEW - CORRIGIDA #####
class UsuarioUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UsuarioEdicaoForm  # Adicione esta linha
    template_name = 'formularios/formulario.html'
    success_url = reverse_lazy('usuario_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Usuário atualizado com sucesso!'
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Por favor, corrija os erros abaixo.'
        )
        return super().form_invalid(form)

##### DELETE VIEW #####
class UsuarioDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'formularios/formulario_exclusao.html'
    success_url = reverse_lazy('usuario_list')

    def delete(self, request, *args, **kwargs):
        messages.success(
            self.request,
            'Usuário excluído com sucesso!'
        )
        return super().delete(request, *args, **kwargs)

##### LIST VIEW #####
class UsuarioListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 10

    def get_queryset(self):
        return User.objects.all().order_by('username')