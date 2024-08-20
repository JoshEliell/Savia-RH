from django.contrib import admin
from .models import Categoria, Subcategoria,Bono,Solicitud,Requerimiento,Puesto, BonoSolicitado

# Register your models here.
admin.site.register(Categoria)

class BonoAdmin(admin.ModelAdmin):
    ordering = ['esquema_subcategoria']
    list_display = ['id','esquema_subcategoria','puesto','distrito','estado','importe']
    search_fields = ['esquema_subcategoria__nombre','puesto','distrito__distrito','importe']
    list_filter = ['esquema_subcategoria','distrito']
    
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ['id','nombre','soporte']
    ordering = ['nombre']
    search_fields = ['id','nombre','soporte']
    
class BonoSolicitadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'solicitud_id', 'trabajador', 'bono', 'cantidad', 'fecha']
    search_fields = ['solicitud__folio','trabajador__nombres', 'trabajador__apellidos', 'bono__esquema_subcategoria__nombre']
    raw_id_fields = ('solicitud', 'trabajador', 'bono')
    list_per_page = 50

class SolicitudAdmin(admin.ModelAdmin):
    list_display = ['id','folio','bono','solicitante','total','fecha_autorizacion']
    search_fields = ['folio','bono__nombre','solicitante__nombres','solicitante__apellidos']
    raw_id_fields = ('solicitante','bono')
    list_filter = ['solicitante__distrito']
    list_per_page = 50

class PuestoAdmin(admin.ModelAdmin):
    list_display = ['id','puesto']
    search_fields = ['id','puesto']
    ordering = ['puesto']
    list_per_page = 100
    
class RequerimientoAdmin(admin.ModelAdmin):
    list_display = ['solicitud_id','url','fecha']
    search_fields = ['solicitud__folio']
    raw_id_fields = ['solicitud'] 
    list_per_page = 100
    
admin.site.register(Bono,BonoAdmin)
admin.site.register(Subcategoria,SubcategoriaAdmin)
admin.site.register(BonoSolicitado,BonoSolicitadoAdmin)
admin.site.register(Solicitud,SolicitudAdmin)
admin.site.register(Puesto,PuestoAdmin)
admin.site.register(Requerimiento,RequerimientoAdmin)