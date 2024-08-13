from django.contrib import admin
from .models import Categoria, Subcategoria,Bono,Solicitud,Requerimiento,Puesto, BonoSolicitado

# Register your models here.
admin.site.register(Categoria)
admin.site.register(Solicitud)
admin.site.register(Requerimiento)
admin.site.register(Puesto)
admin.site.register(BonoSolicitado)

class BonoAdmin(admin.ModelAdmin):
    ordering = ['esquema_subcategoria']
    list_display = ['id','esquema_subcategoria','puesto','distrito','estado','importe']
    search_fields = ['esquema_subcategoria__nombre','puesto','distrito__distrito','importe']
    list_filter = ['esquema_subcategoria','distrito']
    
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ['id','nombre','soporte']

admin.site.register(Bono,BonoAdmin)
admin.site.register(Subcategoria,SubcategoriaAdmin)