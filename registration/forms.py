from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserCreationFormWithEmail(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido, 254 caracteres como maximo y debe ser válido")
    username = forms.CharField(required=True, help_text="Maximo 12 caracteres")
    
    class Meta():
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    
    
class ResetPasswordForm(forms.Form):
    email = forms.EmailField(label="Email", required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Escribe tu email'}
    ), min_length=3, max_length=100)
  