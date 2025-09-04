from django.views.generic import TemplateView
from django.utils import timezone
from livros.models import Livro,Emprestimo

# Create your views here.


class PaginaView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['livros_disponiveis'] = Livro.objects.filter(disponivel=True).count()
        context['emprestimos_ativos'] = Emprestimo.objects.filter(status='ativo').count()
        context['emprestimos_atrasados'] = Emprestimo.objects.filter(status='atrasado').count()

        return context
