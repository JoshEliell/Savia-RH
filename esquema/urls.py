from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    #Bono Varillero - solicitudes
    path('bonos/', views.inicio, name='bono_inicio'),
    path('bonos_varillero/', views.listarBonosVarilleros, name='listarBonosVarilleros'),
    path('bonos_varillero/crear_solicitud/', views.crearSolicitudBonos, name="crearSolicitudBonos"),
    path('bonos_varillero/<int:solicitud_id>/ver-detalles-solicitud/', views.verDetallesSolicitud, name="verDetalleSolicitud"),
    path('bonos_varillero/<int:solicitud>/realizar-cambios-solicitud/', views.verificarSolicitudBonosVarilleros, name="verificarSolicitudBonosVarilleros"),
    path('bonos_varillero/bonos-aprobados', views.listarBonosVarillerosAprobados, name='listarBonosVarillerosAprobados'),
    path('bonos_varillero/generar-reporte', views.generarReporteBonosVarillerosAprobados, name="generarReporteBonosVarillerosAprobados"),
    #Modulo crear bonos
    #path('bonos_varillero/tabulador_bonos',views.tabuladorBonos, name="tabuladorBonos"),
    #api
    path('remover_bono/<int:bono_id>/',views.removerBono, name="remover-bono"),
    path('remover_archivo/<int:archivo_id>/',views.removerArchivo),
    path('ajax/load-puestos/', views.get_puestos, name='ajax_load_puestos'),
    
]