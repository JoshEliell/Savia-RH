from django import forms
from django.shortcuts import render,get_object_or_404
from proyecto.models import Perfil,UserDatos
from .models import Solicitud,BonoSolicitado,Subcategoria,Puesto,Requerimiento,Bono
from revisar.models import AutorizarSolicitudes,Estado
from datetime import datetime


def usuarioLogueado(request):
    usuario = get_object_or_404(UserDatos,user_id = request.user.id)
    return usuario.distrito.id

#ESQUEMA BONOS
class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['bono','comentario']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que el campo 'comentario' no sea requerido
        self.fields['comentario'].required = False
        
class BonoSolicitadoForm(forms.ModelForm):
    class Meta:
        model = BonoSolicitado
        fields = ['trabajador','cantidad']
    
    def __init__(self, *args, **kwargs):
        super(BonoSolicitadoForm, self).__init__(*args, **kwargs)
        self.fields['cantidad'].widget.attrs['readonly'] = True
        self.fields['cantidad'].required = True
        
class BonoSolicitadoPuestoForm(forms.Form):
    puesto = forms.ModelChoiceField(queryset=Puesto.objects.none(), required=True)        

#Perfiles de superintendente operativo, administrativo - tipo_perfil_id = 6 y 12
class AutorizarSolicitudForm(forms.ModelForm):
    
    class Meta:
        model = AutorizarSolicitudes
        fields = ['perfil']
        error_messages = {
            'perfil': {
                'required': 'Debe seleccionar un perfil',
            },
        }
        
    """
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extrae el usuario del kwargs
        super().__init__(*args, **kwargs)
        if user is not None:
            # Construye el queryset usando el usuario
            #distrito_id = user.distrito
            self.fields['perfil'].queryset = Perfil.objects.all()
    """        
"""  
class BonoSolicitadoForm(forms.ModelForm):
    class Meta:
        model = BonoSolicitado
        fields = ['trabajador','puesto','cantidad']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #se filtra el puesto para el bono varillero
        self.fields['puesto'].queryset = Puesto.objects.all()
        #para que la cantidad no sea editable
        self.fields['cantidad'].widget.attrs['readonly'] = 'readonly'
        #self.fields['cantidad'].widget.attrs['required'] = 'required'
"""
 
class RequerimientoForm(forms.ModelForm):    
    class Meta:
        model = Requerimiento
        fields = ['url']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['url'].widget.attrs['multiple'] = 'multiple'

#REVISION AUTORIZACIONES
class AutorizarSolicitudesUpdateForm(forms.ModelForm):
    class Meta:
        model = AutorizarSolicitudes
        fields = ['comentario']
    
    comentario = forms.CharField(required=False)
    
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #se filtran los estados de las autorizaciones
       
        self.fields['estado'].queryset = Estado.objects.all().order_by('tipo')
    """   
class AutorizarSolicitudesGerenteUpdateForm(forms.ModelForm):
    class Meta:
        model = AutorizarSolicitudes
        fields = ['estado','comentario']
    
    comentario = forms.CharField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #se filtran los estados de las autorizaciones
       
        self.fields['estado'].queryset = Estado.objects.filter(id__in=[1,2,3,]).order_by('tipo')