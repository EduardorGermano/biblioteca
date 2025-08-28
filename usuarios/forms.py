from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class UsuarioCadastroForm(UserCreationForm):


    email = forms.EmailField(required=True, help_text="Informe um email válido.")


    # Define o model e os fields que vão aparecer na tela
    class Meta:
        model = User
        # Esses dois passwords são para verificar se as senhas são iguais
        fields = ['username', 'email', 'password1', 'password2']


    # O metodo clean no forms serve de validação para os campos
    def clean_email(self):
        # recebe o email do formulário
        email = self.cleaned_data.get('email')
        # Verifica se já existe algum usuário com este email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está em uso.")
        return email
    
class UsuarioEdicaoForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label='Nome')
    last_name = forms.CharField(required=True, label='Sobrenome')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']