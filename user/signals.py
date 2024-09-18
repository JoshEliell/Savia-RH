from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from proyecto.models import UserDatos
from django.contrib.auth import logout
from django.shortcuts import redirect

#Despues de haber iniciado sesión lanza el template para seleccionar el perfil
@receiver(user_logged_in)
def seleccionar_perfil_sesion(sender, request, user, **kwargs):
    return redirect('seleccionar_perfil')
     
#Limpia la variable de sesión 'usuario_datos' cuando el usuario cierra sesión.
@receiver(user_logged_out)
def limpiar_sesion(sender, request, user, **kwargs):
    if 'usuario_datos' in request.session:
        del request.session['usuario_datos']