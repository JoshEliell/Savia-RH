from django.contrib import admin

# Register your models here.
from .models import Prenomina, Incidencia, IncidenciaRango, PrenominaIncidencias, TipoAguinaldo, Aguinaldo

class PrenominaAdmin(admin.ModelAdmin):
    #ordering = ['catorcena']
    list_display = ('id','empleado','catorcena',)
    search_fields = ('empleado__status__perfil__numero_de_trabajador','empleado__status__perfil__nombres','empleado__status__perfil__apellidos')
    list_filter = ('empleado__status__perfil__distrito'),

class IncidenciaAdmin(admin.ModelAdmin):
    ordering = ['id',]
    list_display = ('tipo','id',)
    
class IncidenciaRangoAdmin(admin.ModelAdmin):
    list_display = ['id','incidencia','empleado','fecha_inicio','fecha_fin','dia_inhabil','soporte','subsecuente','complete']
    raw_id_fields = ('incidencia', 'empleado', 'dia_inhabil')
    search_fields = ['incidencia__tipo','empleado__status__perfil__numero_de_trabajador','empleado__status__perfil__nombres','empleado__status__perfil__apellidos']
    
class PrenominaIncidenciasAdmin(admin.ModelAdmin):
    list_display = ['id','fecha','incidencia','comentario','soporte','prenomina_id']
    raw_id_fields = ('prenomina', 'incidencia', 'incidencia_rango')
    ordering = ['prenomina']
    search_fields = ['prenomina__empleado__status__perfil__nombres','prenomina__empleado__status__perfil__apellidos','prenomina__empleado__status__perfil__numero_de_trabajador']
    list_filter = ('prenomina__empleado__status__perfil__distrito'),
    
class AguinaldoAdmin(admin.ModelAdmin):
    list_display = ['id','empleado','monto','tipo','mes','catorcena']
    search_fields = ['empleado__status__perfil__numero_de_trabajador','empleado__status__perfil__nombres','empleado__status__perfil__apellidos']
    raw_id_fields = ('empleado', 'catorcena', 'tipo')
    
admin.site.register(Prenomina, PrenominaAdmin)
admin.site.register(Incidencia, IncidenciaAdmin)
admin.site.register(IncidenciaRango, IncidenciaRangoAdmin)
admin.site.register(PrenominaIncidencias,PrenominaIncidenciasAdmin)
admin.site.register(Aguinaldo, AguinaldoAdmin)
admin.site.register(TipoAguinaldo)