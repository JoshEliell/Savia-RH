from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from proyecto.models import UserDatos
from django.contrib.auth import logout
from django.shortcuts import redirect

@receiver(user_logged_in)
def seleccionar_perfil_sesion(sender, request, user, **kwargs):
    #Establece una variable de sesión después de que el usuario inicie sesión.
    try:
        # Realiza la consulta para obtener los datos del usuario
        usuario_datos = UserDatos.objects.get(user_id=user.id, activo=True, perfil__distrito_id=user.perfil.distrito.id)
        # Almacena los datos en la sesión
        request.session['usuario_datos'] = {
            'user_id': usuario_datos.user.id,
            'perfil_id': usuario_datos.perfil.id,
            'distrito_id': usuario_datos.distrito.id,
            'tipo_id': usuario_datos.tipo.id,
            'rol': usuario_datos.tipo.nombre,
            
        }
        
    except Exception as e:
        #Finalizar la session 
        logout(request)
        
@receiver(user_logged_out)
def limpiar_sesion(sender, request, user, **kwargs):
    #Limpia la variable de sesión 'usuario_datos' cuando el usuario cierra sesión.
    if 'usuario_datos' in request.session:
        del request.session['usuario_datos']