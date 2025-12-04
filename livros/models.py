from datetime import timedelta
from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone  

# Create your models here.
class Autor(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome do Autor')

    def __str__(self):
        return self.nome
    
class Genero(models.Model):
    nome = models.CharField(max_length=50, verbose_name='Nome do Gênero')

    def __str__(self):
        return self.nome

class Livro(models.Model):
    titulo = models.CharField(max_length=200 , verbose_name='Título')
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT, verbose_name='Autor')
    genero = models.ForeignKey(Genero, on_delete=models.PROTECT, verbose_name='Gênero')
    data_aquisicao = models.DateField(null=True, blank=True, verbose_name='Data de Aquisição')
    disponivel = models.BooleanField(default=True, verbose_name='Disponível', choices=[
        (True, 'Sim'),
        (False, 'Não'),
    ])
    estado = models.CharField(max_length=20, choices=[
        ('Novo', 'Novo'),
        ('Usado', 'Usado'),
        ('Danificado', 'Danificado'),
    ], default='Novo', verbose_name='Estado')

    def __str__(self):
        return self.titulo

class Emprestimo(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT, verbose_name='Livro')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuário')
    data_emprestimo = models.DateTimeField(auto_now_add=True, verbose_name='Data do Empréstimo')
    data_devolucao_prevista = models.DateTimeField(verbose_name='Data de Devolução Prevista')
    data_devolucao_real = models.DateTimeField(null=True, blank=True, verbose_name='Data de Devolução Real')
    status = models.CharField(max_length=20, choices=[
        ('ativo', 'Ativo'),
        ('devolvido', 'Devolvido'),
        ('atrasado', 'Atrasado'),
    ], default='ativo', verbose_name='Status')
    
    class Meta:
        verbose_name = 'Empréstimo'
        verbose_name_plural = 'Empréstimos'
        ordering = ['-data_emprestimo']

    def __str__(self):
        return f"{self.livro.titulo} - {self.usuario.username}"

    def save(self, *args, **kwargs):
        # Se for um novo empréstimo, define a data de devolução prevista
        if not self.pk:
            self.data_devolucao_prevista = timezone.now() + timedelta(days=14)
            
        # Atualiza o status baseado nas datas
        if self.data_devolucao_real:
            self.status = 'devolvido'
        elif timezone.now() > self.data_devolucao_prevista and self.status == 'ativo':
            self.status = 'atrasado'
            
        super().save(*args, **kwargs)
        
        # Atualiza a disponibilidade do livro
        if self.data_devolucao_real:
            self.livro.disponivel = True
        else:
            self.livro.disponivel = False
        self.livro.save()

    def clean(self):
        # Impede empréstimo de livro não disponível
        if not self.livro.disponivel and not self.data_devolucao_real:
            raise ValidationError('Este livro não está disponível para empréstimo')

    @property
    def dias_atraso(self):
        if self.status == 'atrasado':
            return (timezone.now() - self.data_devolucao_prevista).days
        return 0

    @property
    def multa(self):
        return self.dias_atraso * 2.00

    def devolver(self):
        self.data_devolucao_real = timezone.now()
        self.status = 'devolvido'
        self.save()