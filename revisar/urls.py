from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    #Bono Varillero
    path('bonos_varillero/<int:solicitud>/autorizar-solicitud', views.autorizarSolicitud, name="autorizarSolicitudes"),
    #Prenominas
    path('Prenominas/solicitudes', views.Tabla_solicitudes_prenomina, name='Prenominas_solicitudes'),
    path('revisar/<int:pk>/', views.Prenomina_Solicitud_Revisar, name='Prenomina_solicitud_revisar'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
