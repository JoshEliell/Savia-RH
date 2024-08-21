from django.contrib import admin
from .models import AutorizarSolicitudes,Estado,AutorizarPrenomina

# Register your models here.
admin.site.register(Estado)

class AutorizarSolicitudesAdmin(admin.ModelAdmin):
    list_display = ['id','solicitud_id','perfil','tipo_perfil','estado','revisar','created_at']
    search_fields = ['solicitud__id','perfil__nombres','perfil__apellidos','tipo_perfil__nombre']
    raw_id_fields = ['solicitud', 'perfil', 'tipo_perfil', 'estado']
    list_per_page = 50
    list_filter = ['estado','tipo_perfil','perfil__distrito']

class AutorizarPrenominaAdmin(admin.ModelAdmin):
    list_display = ['id','perfil','tipo_perfil','estado','prenomina_id']
    search_fields = ['perfil__nombres','perfil__apellidos','tipo_perfil__nombre','prenomina__empleado__status__perfil__nombres','prenomina__empleado__status__perfil__apellidos']
    raw_id_fields = ['prenomina', 'perfil', 'tipo_perfil', 'estado']
    list_per_page = 50
    list_filter = ['perfil__distrito']
    
admin.site.register(AutorizarSolicitudes, AutorizarSolicitudesAdmin)
admin.site.register(AutorizarPrenomina, AutorizarPrenominaAdmin)
