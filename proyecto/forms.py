from django import forms
from proyecto.models import Perfil, Status, Costo, DatosBancarios, Bonos, Uniformes, Vacaciones, Economicos, DatosISR, TablaVacaciones, Empleados_Batch, Catorcenas, Proyecto, SubProyecto
from proyecto.models import Status_Batch, Uniforme, Costos_Batch, Bancarios_Batch
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto','numero_de_trabajador','empresa','distrito','nombres',
                'apellidos','fecha_nacimiento','correo_electronico','proyecto','subproyecto',]

class PerfilDistritoForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto','numero_de_trabajador','empresa','nombres',
                'apellidos','fecha_nacimiento','correo_electronico','proyecto','subproyecto',]

class PerfilUpdateForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto','empresa','distrito','nombres',
                'apellidos','fecha_nacimiento','correo_electronico','proyecto','subproyecto',]

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['perfil','registro_patronal','nss','curp','rfc','profesion',
                'no_cedula','nivel','tipo_de_contrato','ultimo_contrato_vence','tipo_sangre',
                'sexo','domicilio','estado_civil','fecha_planta_anterior','fecha_planta','telefono',]

class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['registro_patronal','nss','curp','rfc','profesion',
                'no_cedula','nivel','tipo_de_contrato','ultimo_contrato_vence','tipo_sangre',
                'sexo','domicilio','estado_civil','fecha_planta_anterior','fecha_planta','telefono',]

class CostoForm(forms.ModelForm):
    class Meta:
        model = Costo
        fields = ['status','puesto','amortizacion_infonavit','fonacot','neto_catorcenal_sin_deducciones',
                'complemento_salario_catorcenal','sueldo_diario','sdi','apoyo_de_pasajes','imms_obrero_patronal',
                'apoyo_vist_familiar','estancia','renta','apoyo_estudios','amv','gasolina','campamento',]


class CostoUpdateForm(forms.ModelForm):
    class Meta:
        model = Costo
        fields = ['puesto','amortizacion_infonavit','fonacot','neto_catorcenal_sin_deducciones',
                'complemento_salario_catorcenal','sueldo_diario','sdi','apoyo_de_pasajes','imms_obrero_patronal',
                'apoyo_vist_familiar','estancia','renta','apoyo_estudios','amv','gasolina','campamento',]

class DatosBancariosForm(forms.ModelForm):
    class Meta:
        model = DatosBancarios
        fields = ['status','no_de_cuenta','numero_de_tarjeta','clabe_interbancaria','banco']

class BancariosUpdateForm(forms.ModelForm):
    class Meta:
        model = DatosBancarios
        fields = ['no_de_cuenta','numero_de_tarjeta','clabe_interbancaria','banco']

class BonosForm(forms.ModelForm):
    class Meta:
        model = Bonos
        fields = ['monto','costo','fecha_bono',]

class BonosUpdateForm(forms.ModelForm):
    class Meta:
        model = Bonos
        fields = ['monto','fecha_bono',]

class UniformesForm(forms.ModelForm):
    class Meta:
        model = Uniformes
        fields = ['fecha_pedido']

class UniformeForm(forms.ModelForm):
    class Meta:
        model = Uniforme
        fields = ['ropa','talla','cantidad']



class VacacionesForm(forms.ModelForm):
    class Meta:
        model = Vacaciones
        fields = ['status','dias_disfrutados','comentario']

class VacacionesUpdateForm(forms.ModelForm):
    class Meta:
        model = Vacaciones
        fields = ['dias_disfrutados','comentario']

class EconomicosForm(forms.ModelForm):
    class Meta:
        model = Economicos
        fields = ['status','fecha','comentario',]

class EconomicosUpdateForm(forms.ModelForm):
    class Meta:
        model = Economicos
        fields = ['fecha','comentario',]

class IsrForm(forms.ModelForm):
    class Meta:
        model = DatosISR
        fields = ['liminf','limsup','cuota','excedente',
                 'p_ingresos','g_ingresos','subsidio',]

class Dias_VacacionesForm(forms.ModelForm):
    class Meta:
        model = TablaVacaciones
        fields = ['years','days',]

class Empleados_BatchForm(forms.ModelForm):
    class Meta:
        model = Empleados_Batch
        fields= ['file_name']

class Status_BatchForm(forms.ModelForm):
    class Meta:
        model = Status_Batch
        fields= ['file_name']

class Costos_BatchForm(forms.ModelForm):
    class Meta:
        model = Costos_Batch
        fields= ['file_name']

class Bancarios_BatchForm(forms.ModelForm):
    class Meta:
        model = Bancarios_Batch
        fields= ['file_name']

class CatorcenasForm(forms.ModelForm):
    class Meta:
        model = Catorcenas
        fields = ['catorcena','fecha_inicial','fecha_final',]
