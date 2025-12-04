from django import forms
from .models import Livro


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ['titulo', 'autor', 'genero', 'data_aquisicao', 'disponivel', 'estado']
        widgets = {
            'data_aquisicao': forms.DateInput(attrs={'type': 'date'}),
        }
