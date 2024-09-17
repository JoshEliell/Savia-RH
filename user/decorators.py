from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# Decorador personalizado para verificar si el usuario está autenticado
def perfil_session_seleccionado(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Verifica si el usuario está autenticado
        if not request.user.is_authenticated:
             return redirect('login') 
             
        # Aqui lo manda a seleccionar el perfil sino hay seleccionado el rol
        userdatos = request.session.get('usuario_datos')    
        if userdatos is None:
            return redirect('seleccionar_perfil')
        
        #Continua a la siguente vista
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view