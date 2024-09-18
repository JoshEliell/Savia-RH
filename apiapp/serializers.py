from rest_framework import serializers
from proyecto.models import Perfil, Empresa, Proyecto, SubProyecto, Distrito

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['empresa']

class DistritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distrito
        fields = ['distrito']

class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = ['proyecto']

class SubProyectoSerializer(serializers.ModelSerializer):
    proyecto = ProyectoSerializer()  # Anidamos el Proyecto para obtener su nombre

    class Meta:
        model = SubProyecto
        fields = ['subproyecto', 'proyecto']
        
class PerfilSerializer(serializers.ModelSerializer):
    empresa = EmpresaSerializer()  # Anidamos Empresa para obtener su nombre
    distrito = DistritoSerializer()  # Anidamos Distrito para obtener su nombre
    proyecto = ProyectoSerializer()  # Anidamos Proyecto para obtener su nombre
    subproyecto = SubProyectoSerializer()  # Anidamos SubProyecto para obtener su nombre y el proyecto relacionado
    correo_vordcab = serializers.EmailField(source='usuario.email', read_only=True)  # Campo personalizado para correo de User
    #activo = serializers.BooleanField(source='baja', read_only=True)  # Mapea 'baja' a 'activo'    No necesario como el boleano te dice si baja=True en vez si es activo

    class Meta:
        model = Perfil
        fields = ['correo_vordcab','baja','numero_de_trabajador', 'empresa', 'distrito', 'division', 'nombres', 'apellidos', 'fecha_nacimiento', 'correo_electronico', 'proyecto', 'subproyecto',]

