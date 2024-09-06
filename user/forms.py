from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth import get_user_model, authenticate
from proyecto.models import UserDatos

#Esta "form" fue creada heredando (inherit) las características de la "UserCreationForm" pero agregándole el "email"
class UserForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username','email','password1','password2']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
    )
    
class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request,
                                           username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
    
class UserDatosForm(forms.ModelForm):
    class Meta:
        model = UserDatos
        fields = ['user_datos']
    
    user_datos = forms.ModelChoiceField(queryset=UserDatos.objects.none())

    def __init__(self, *args, **kwargs):
        # Asegúrate de llamar al __init__ del formulario padre
        super().__init__(*args, **kwargs)

        # Obtener el perfil del usuario actual, si es necesario
        user = self.initial.get('user')  # O cualquier otra forma de obtener el usuario actual
        perfil = user.perfil if user else None
        if perfil:
                # Obtener los UserDatos asociados al perfil del usuario
                roles = UserDatos.objects.filter(perfil=perfil, activo=True)
                self.fields['user_datos'].queryset = roles
        # Personalizar las opciones del campo 'user_datos'
                self.fields['user_datos'].widget.choices = [(obj.id, f"{obj.perfil.nombres} {obj.perfil.apellidos} {obj.tipo.tipo} {obj.distrito.nombre}") for obj in roles]
        
        
