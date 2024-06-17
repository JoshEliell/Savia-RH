from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from proyecto.models import UserDatos, Perfil, Catorcenas, Costo, TablaFestivos, Vacaciones, Economicos, Economicos_dia_tomado, Vacaciones_dias_tomados, Empresa, Solicitud_vacaciones, Solicitud_economicos, Trabajos_encomendados
from proyecto.models import TablaVacaciones,SalarioDatos,DatosISR

from django.db import models
from django.db.models import Subquery, OuterRef, Q
from revisar.models import AutorizarPrenomina, Estado
from proyecto.filters import CostoFilter
from .models import Prenomina,PrenominaIncidencias, IncidenciaRango
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
import datetime 
from dateutil import parser
from dateutil.relativedelta import relativedelta
import os

from datetime import timedelta, date
from .filters import PrenominaFilter
import math

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
#Excel
from openpyxl import Workbook
import openpyxl
from openpyxl.chart import PieChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.chart.label import DataLabelList
from openpyxl.drawing.image import Image
from openpyxl.styles import NamedStyle, Font, PatternFill
from openpyxl.utils import get_column_letter
from django.db.models.functions import Concat
from django.db.models import Value
from django.db.models import Sum
from django.db.models import Count
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.http import HttpResponseRedirect

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter,A4,landscape
import io
from reportlab.lib import colors
from reportlab.lib.colors import Color, black, blue, red, white
from reportlab.platypus import BaseDocTemplate, Frame, Paragraph, NextPageTemplate, PageBreak, PageTemplate,Table, SimpleDocTemplate,TableStyle, KeepInFrame, Spacer
import textwrap
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from django.http import FileResponse
from django.core.files.base import ContentFile

from decimal import Decimal 
import calendar
from esquema.models import BonoSolicitado
from django.db.models import Sum

from proyecto.models import Variables_imss_patronal
from proyecto.models import SalarioDatos

from .forms import PrenominaIncidenciasFormSet,IncidenciaRangoForm
import time

from calculos.utils import excel_estado_prenomina

# Create your views here.

#funcion para obtener la catorcena actual
def obtener_catorcena():
    fecha_actual = datetime.date.today()
    catorcena_actual = Catorcenas.objects.filter(fecha_inicial__lte=fecha_actual, fecha_final__gte=fecha_actual).first()
    return catorcena_actual

def registrar_rango_incidencias(request,pk):    
    if request.method == 'POST':
        #catorcena
        catorcena_actual = obtener_catorcena()
        #RH
        user_filter = UserDatos.objects.get(user=request.user)
        #nombre = Perfil.objects.get(numero_de_trabajador = user_filter.numero_de_trabajador, distrito = user_filter.distrito)
        #Empleado
        #costo = Costo.objects.get(id=pk)
        prenomina = Prenomina.objects.get(empleado=pk,catorcena = catorcena_actual.id)
        #Se trae el formulario de las incapacidades para ser validado
        incidencias_form = IncidenciaRangoForm(request.POST, request.FILES)
        if incidencias_form.is_valid():
            #validaciones a partir de la fecha de inicio y fecha fin
            fecha_start = incidencias_form.cleaned_data['fecha_inicio']
            fecha_end = incidencias_form.cleaned_data['fecha_fin']
            
            if fecha_start > fecha_end:
                 return JsonResponse({'poscondicion': 'La fecha de inicio debe ser menor a la fecha final'}, status=422)
            
            if fecha_start < catorcena_actual.fecha_inicial:
                return JsonResponse({'poscondicion': 'No puedes agregar una fecha anterior de la catorcena actual'}, status=422)
            
            #Busca si existe al menos una vacacion en el rango de fechas: inicio - fin y valida
            vacaciones = Vacaciones_dias_tomados.objects.filter(
                prenomina__status=prenomina.empleado.status,
                fecha_inicio__lte=fecha_end,
                fecha_fin__gte=fecha_start
            ).values('id').exists()
            
            #validacion de vacaciones
            if vacaciones:
                return JsonResponse({'poscondicion': 'Ya existen vacaciones dentro del rango de fechas especificado'}, status=422)
            
            #Busca si existe al menos un dia festivo en el rango de fechas: inicio - fin y valida
            festivos = TablaFestivos.objects.filter(dia_festivo__range=[fecha_start, fecha_end]).values('id').exists()  
            if festivos:
                return JsonResponse({'poscondicion': 'Ya existen dias festivos dentro del rango de fechas especificado'}, status=422) 
            
            #Busca si existe al menos un dia economico en el rango de fechas: inicio - fin y valida
            economicos = Economicos_dia_tomado.objects.filter(fecha__range=[fecha_start, fecha_end]).values('id').exists()  
            if economicos:
                return JsonResponse({'poscondicion': 'Ya existen economicos dentro del rango de fechas especificado'}, status=422)
            
            #Busca si existe al menos una incidencia de rango en las fechas: inicio - fin y valida
            incidencias = PrenominaIncidencias.objects.filter(prenomina__empleado_id=pk,fecha__range=[fecha_start, fecha_end]).values('id').exists()   
            if incidencias:
                return JsonResponse({'poscondicion': 'Ya existen incidencias dentro del rango de fechas especificado'}, status=422)
            
            #Cumple la validacion - Se guarda el rango de incidencia
            incidencia_rango = incidencias_form.save(commit=False)
            incidencia_rango.soporte = request.FILES['soporte'] 
            incidencia_rango.empleado_id = pk #este es el id del costo del empleado
            incidencia_rango.save()  
            
            fecha_actual = incidencia_rango.fecha_inicio #punto de inicio
            fecha_fin = min(incidencia_rango.fecha_fin, prenomina.catorcena.fecha_final) #toma la fecha fin mas chica entre las dos fechas para que solo se registren las que caen en la cat
            
            #se empieza a extraer los datos de IncidenciaRango para almacenarlos en el modelo PrenominaIncidencias
            while fecha_actual <= fecha_fin:
                incidencia = incidencia_rango.incidencia_id
                comentario = incidencia_rango.comentario
                soporte = incidencia_rango.soporte
                
                if fecha_actual.weekday() == (incidencia_rango.dia_inhabil_id - 1): 
                    if (incidencia_rango.dia_inhabil_id - 1) == 6:# se resta 1 para obtener el dia domingo
                        incidencia = 5 #domingo
                        comentario = None
                        soporte = None
                    else:
                        incidencia = 2 #descanso
                        comentario = None
                        soporte = None
                        
                registro_prenomina, creado = PrenominaIncidencias.objects.update_or_create(
                    prenomina=prenomina,
                    fecha=fecha_actual,
                    defaults={
                        'comentario': comentario, 
                        'soporte': soporte,
                        'incidencia_id': incidencia,
                        'incidencia_rango':incidencia_rango,                        
                    }
                )
                fecha_actual += timedelta(days=1)
                
            return JsonResponse({'success': 'Agregado correctamente'}, status=200)
        
        #validaciones del formulario
        else:
            validacion = None
            #se obtienen los valores de validaicones uno por uno
            errores = dict(incidencias_form.errors.items())
            for field, error_list in errores.items():
                  for error in error_list:
                      print(error)
                      validacion = error
                      
            # Prepara la respuesta JSON con los errores de validacion
            response_data = {
                'validaciones': validacion,
            }
            
            #Se envia los errores de validaciones al cliente
            return JsonResponse(response_data, status=422)
        
@login_required(login_url='user-login')
def Tabla_prenomina(request):
    start_time = time.time()  # Registrar el tiempo de inicio
    user_filter = UserDatos.objects.get(user=request.user)
    revisar_perfil = Perfil.objects.get(distrito=user_filter.distrito,numero_de_trabajador=user_filter.numero_de_trabajador)
    empresa_faxton = Empresa.objects.get(empresa="Faxton")
    if user_filter.tipo.nombre == "RH":
        
        #llamar la fucion para obtener la catorcena actual
        catorcena_actual = obtener_catorcena()
        
        #para traer los empleados segun el filtro
        if revisar_perfil.empresa == empresa_faxton:
            costo = Costo.objects.filter(complete=True, status__perfil__baja=False,status__perfil__empresa=empresa_faxton).order_by("status__perfil__numero_de_trabajador")
        elif user_filter.distrito.distrito == 'Matriz':
            costo = Costo.objects.filter(complete=True, status__perfil__baja=False).order_by("status__perfil__numero_de_trabajador")
        else:
            costo = Costo.objects.filter(status__perfil__distrito=user_filter.distrito, complete=True,  status__perfil__baja=False).order_by("status__perfil__numero_de_trabajador")

        prenominas = Prenomina.objects.filter(empleado__in=costo,catorcena=catorcena_actual.id).order_by("empleado__status__perfil__numero_de_trabajador")
        #prenominas = Prenomina.objects.filter(empleado__in=costo,catorcena = catorcena_actual.id).order_by("empleado__status__perfil__numero_de_trabajador").prefetch_related('incidencias')
        festivos = TablaFestivos.objects.filter(dia_festivo__range=(catorcena_actual.fecha_inicial, catorcena_actual.fecha_final))
        #crear las prenominas actuales si es que ya es nueva catorcena
        nuevas_prenominas = []
        for empleado in costo:
            #checar si existe prenomina para el empleado en la catorcena actual
            prenomina_existente = prenominas.filter(empleado=empleado).exists()
            #si no existe crear una nueva prenomina
            if not prenomina_existente:
                nueva_prenomina = Prenomina(empleado=empleado, catorcena=catorcena_actual)
                nuevas_prenominas.append(nueva_prenomina) 
        if nuevas_prenominas:
            Prenomina.objects.bulk_create(nuevas_prenominas)              
        #costo_filter = CostoFilter(request.GET, queryset=costo)
        #costo = costo_filter.qs
        #prenominas = Prenomina.objects.filter(empleado__in=costo,catorcena = catorcena_actual.id).order_by("empleado__status__perfil__numero_de_trabajador").prefetch_related('incidencias')
        
        prenomina_filter = PrenominaFilter(request.GET, queryset=prenominas)
        prenominas = prenomina_filter.qs

        #para verificar las autotizaciones
        for prenomina in prenominas:
            ultima_autorizacion = AutorizarPrenomina.objects.filter(prenomina=prenomina).order_by('-updated_at').first() #Ultimo modificado

            if ultima_autorizacion is not None:
                prenomina.valor = ultima_autorizacion.estado.tipo #Esta bien como agarra el dato de RH arriba que es el primero
            prenomina.estado_general = determinar_estado_general(request,ultima_autorizacion)

        if request.method =='POST' and 'Autorizar' in request.POST:
            if user_filter.tipo.nombre ==  "RH":
                prenominas_filtradas = [prenom for prenom in prenominas if prenom.estado_general == 'RH pendiente (rechazado por Controles técnicos)' or prenom.estado_general == 'RH pendiente (rechazado por Gerencia)' or prenom.estado_general == 'Sin autorizaciones']
                if prenominas_filtradas:
                    # Llamar a la función Autorizar_gerencia con las prenominas filtradas
                    return Autorizar_general(request,prenominas_filtradas, user_filter,catorcena_actual)
                else:
                    # Si no hay prenominas que cumplan la condición, manejar según sea necesario
                    messages.error(request,'Ya se han autorizado todas las prenominas pendientes')
        
        if request.method =='POST' and 'Excel' in request.POST:
            #return Excel_estado_prenomina(request,prenominas, user_filter)
            return excel_estado_prenomina(request,prenominas,user_filter)
        if request.method =='POST' and 'Excel2' in request.POST:
            return Excel_estado_prenomina_formato(request,prenominas, user_filter)
        
        p = Paginator(prenominas, 50)
        page = request.GET.get('page')
        salidas_list = p.get_page(page)

        context = {
            'prenomina_filter':prenomina_filter,
            'salidas_list': salidas_list,
            'prenominas':prenominas
        }
        end_time = time.time()  # Registrar el tiempo de finalización
        print(f"Tiempo total de carga de la página: {end_time - start_time} segundos")
        return render(request, 'prenomina/Tabla_prenomina.html', context)
    else:
        return render(request, 'revisar/403.html')

@login_required(login_url='user-login')
def Autorizar_general(request,prenominas, user_filter, catorcena_actual):
    if request.user.is_authenticated:
        nombre = Perfil.objects.get(numero_de_trabajador=user_filter.numero_de_trabajador, distrito=user_filter.distrito)
        festivos = TablaFestivos.objects.filter(dia_festivo__range=[catorcena_actual.fecha_inicial, catorcena_actual.fecha_final]) #festivos en la catorcena actual
        for prenomina in prenominas:    
            incidencias = PrenominaIncidencias.objects.filter(
                    prenomina__empleado_id = prenomina.empleado_id, 
                    fecha__range=(catorcena_actual.fecha_inicial, catorcena_actual.fecha_final))
            if not incidencias.exists(): 
                #obtener los queries para su posterior llenado
                incidencias_rango = IncidenciaRango.objects.filter(empleado_id=prenomina.empleado_id,fecha_inicio__lte=catorcena_actual.fecha_final,fecha_fin__gte=catorcena_actual.fecha_inicial)

                if incidencias_rango:
                    #si te das cuenta siempre al brincar a una catorcena simpre sera de una incidencia es decir que si de castigo se brinca a la otra cat, solo habra de castigo y no puedes registrar dos rangos en una
                    for incidencia_rango in incidencias_rango:
                        fecha_actual = incidencia_rango.fecha_fin
                        fecha_fin = incidencia_rango.fecha_fin
                                    
                    fecha_actual = incidencia_rango.fecha_inicio #punto de inicio
                    fecha_fin = min(incidencia_rango.fecha_fin, prenomina.catorcena.fecha_final)#toma la fecha mas chica entre las dos fechas
                    
                    while fecha_actual <= fecha_fin:
                        incidencia = incidencia_rango.incidencia_id
                        comentario = incidencia_rango.comentario
                        soporte = incidencia_rango.soporte
                        
                        if fecha_actual.weekday() == (incidencia_rango.dia_inhabil_id - 1): 
                            #print(fecha_actual.weekday())
                            if (incidencia_rango.dia_inhabil_id - 1) == 6:# se resta 1 para obtener el dia domingo
                                incidencia = 5 #domingo
                                comentario = None
                                soporte = None
                            else:
                                incidencia = 2 #descanso
                                comentario = None
                                soporte = None
                                
                        registro_prenomina, creado = PrenominaIncidencias.objects.update_or_create(
                        prenomina=prenomina,
                            fecha=fecha_actual,
                            defaults={
                                'comentario': comentario, 
                                'soporte': soporte,
                                'incidencia_id': incidencia,
                                'incidencia_rango':incidencia_rango,                        
                            }
                        )
                        fecha_actual += timedelta(days=1)
                for festivo in festivos:
                    registro, created = PrenominaIncidencias.objects.update_or_create(
                        prenomina_id=prenomina.id,
                        fecha=festivo.dia_festivo,
                        defaults={
                            'incidencia_id': 13 #festivo
                        }
                    )
            economicos = Economicos_dia_tomado.objects.filter(prenomina__status=prenomina.empleado.status, fecha__range=[catorcena_actual.fecha_inicial, catorcena_actual.fecha_final], complete = False)
            vacaciones = Vacaciones_dias_tomados.objects.filter(prenomina__status=prenomina.empleado.status,fecha_inicio__lte=catorcena_actual.fecha_final,fecha_fin__gte=catorcena_actual.fecha_inicial) 
            for economico in economicos:
                registro, created = PrenominaIncidencias.objects.update_or_create(
                    prenomina_id=prenomina.id,
                    fecha=economico.fecha,
                    defaults={
                        'incidencia_id': 14 # economico
                    }
                )

            for vacacion in vacaciones:
                    #se ajusta la fecha de acuerdo a la catorcena
                    fecha_inicio = max(vacacion.fecha_inicio, prenomina.catorcena.fecha_inicial)
                    fecha_fin = min(vacacion.fecha_fin, prenomina.catorcena.fecha_final)
                    #se considera el dia inhabil (descanso)       
                    dia_inhabil = vacacion.dia_inhabil_id
                    
                    fecha = fecha_inicio
                    incidencia = 0
                    #sacar las fechas
                    while fecha_inicio <= fecha_fin:
                        if fecha_inicio <= fecha <= fecha_fin:
                            incidencia = 15 # vacacion
                            #verifica si es domingo o descanso
                            if fecha_inicio.weekday() == (dia_inhabil - 1): 
                                if (dia_inhabil - 1) == 6:# se resta 1 para obtener el dia domingo
                                    incidencia = 5 #domingo
                                else:
                                    incidencia = 2 #descanso
                            elif fecha_inicio in [festivo.dia_festivo for festivo in festivos]:
                                incidencia = 13 #festivo:
                        registro, created = PrenominaIncidencias.objects.update_or_create(
                            prenomina_id=prenomina.id,
                            fecha=fecha,
                            defaults={
                            'incidencia_id': incidencia
                            }
                        )  
                        
                        #se agregar un dia para realizar el recorrido de la fecha          
                        fecha_inicio += timedelta(days=1)
                        fecha +=   timedelta(days=1)
            descansos = PrenominaIncidencias.objects.filter(
                prenomina__empleado_id=prenomina.empleado_id, 
                incidencia__id__in=[6, 5, 2],
                fecha__range=(catorcena_actual.fecha_inicial, catorcena_actual.fecha_final))
            
            if not descansos.exists():
                domingos = []
                fecha = catorcena_actual.fecha_inicial
                while fecha <= catorcena_actual.fecha_final:
                    if fecha.weekday() == 6:  # Domingo
                        domingos.append(fecha)
                    fecha += timedelta(days=1)

                for domingo in domingos[:2]:  #dos domingos
                    PrenominaIncidencias.objects.create(
                        prenomina=prenomina,
                        fecha=domingo,
                        incidencia_id=5,  # Domingo
                        comentario=None,
                        soporte=None,
                        incidencia_rango=None
                    )
            else:
                if descansos.count() == 1:
                    descanso = descansos.first()
                    dia_semana = descanso.fecha.weekday()

                    for i in range((catorcena_actual.fecha_final - catorcena_actual.fecha_inicial).days + 1):
                        fecha = catorcena_actual.fecha_inicial + timedelta(days=i)
                        if fecha.weekday() == dia_semana and fecha != descanso.fecha:
                            PrenominaIncidencias.objects.create(
                                prenomina=prenomina,
                                fecha=fecha,
                                incidencia_id=descanso.incidencia_id,  # Mismo tipo de incidencia
                                comentario=None,
                                soporte=None,
                                incidencia_rango=None
                            )
                            break


                

            revisado, created = AutorizarPrenomina.objects.get_or_create(prenomina=prenomina, tipo_perfil=user_filter.tipo) #Checa si existe autorización de su perfil y si no lo crea 
            revisado.estado = Estado.objects.get(tipo="aprobado")
            nombre = Perfil.objects.get(numero_de_trabajador=user_filter.numero_de_trabajador, distrito=user_filter.distrito)
            revisado.perfil = nombre
            revisado.comentario = 'Aprobación general'
            revisado.save()
        messages.success(request, 'Prenominas pendientes autorizadas automaticamente')
        return redirect('Prenomina')  # Cambia 'ruta_a_redirigir' por la URL a la que deseas redirigir después de autorizar las prenóminas
    
@login_required(login_url='user-login')
def PrenominaRevisar(request, pk):
    user_filter = UserDatos.objects.get(user=request.user)
    if user_filter.tipo.id == 4: #Perfil RH
        start_time = time.time()  # Registrar el tiempo de inicio
        #llamar la fucion para obtener la catorcena actual
        catorcena_actual = obtener_catorcena()
        
        #obtener el empleado respecto a su prenomina     
        costo = Costo.objects.get(id=pk)
        prenomina = Prenomina.objects.get(empleado=costo,catorcena = catorcena_actual.id)
        
        #flujo de las autorizaciones
        autorizacion1 = prenomina.autorizarprenomina_set.filter(tipo_perfil__nombre="Control Tecnico").first()
        autorizacion2 = prenomina.autorizarprenomina_set.filter(tipo_perfil__nombre="Gerencia").first()
        
        if request.method == 'POST':
            #Para guardar los datos en la prenomina
            if 'guardar_cambios' in request.POST:
                prenomina_form = PrenominaIncidenciasFormSet(request.POST) #se obtienen instacias de formularios (14)
                if prenomina_form.is_valid():
                    for form in prenomina_form:
                        #se extren los datos 
                        asistencia = form.cleaned_data['incidencia']
                        if asistencia.id != 16: #no se registrar el 16 - asistencias
                            fecha = form.cleaned_data['fecha']
                            comentario = form.cleaned_data['comentario']
                            incidencia = form.cleaned_data['incidencia']
                            
                            registro_prenomina, creado = PrenominaIncidencias.objects.update_or_create(
                                prenomina=prenomina,
                                fecha=fecha,
                                defaults={
                                    'comentario': comentario, 
                                    'incidencia': incidencia
                                }
                            )   
                messages.success(request,"Se ha guardado la prenomina")         
                return redirect(request.META.get('HTTP_REFERER'))
            
            #Para eliminar los datos en la prenomina
            if 'eliminar_cambios' in request.POST:
                prenomina_form = PrenominaIncidenciasFormSet(request.POST) #se obtienen instacias de formularios (14)
                if prenomina_form.is_valid():
                    for form in prenomina_form:
                        if form.cleaned_data.get('DELETE'):
                            id = form.cleaned_data['id']
                            rango = form.cleaned_data['id_rango']
                            
                            # Si el formulario está marcado para eliminación, eliminar el registro
                            if id and rango is not None:
                                buscar_rango = IncidenciaRango.objects.filter(pk=rango)
                                for rango in buscar_rango:
                                    rango_fecha_inicio = rango.fecha_inicio
                                    archivo = rango.soporte.path

                                if rango_fecha_inicio >= catorcena_actual.fecha_inicial:
                                    PrenominaIncidencias.objects.filter(incidencia_rango_id=rango).delete()
                                    # Eliminar el archivo si existe
                                    if os.path.exists(archivo):
                                        os.remove(archivo)
                                    buscar_rango.delete()
                                else:
                                    messages.info(request,"No se puede eliminar estas incidencias, se registraron desde la prenomina anterior")         
                                    return redirect(request.META.get('HTTP_REFERER'))
                                    
                            else:
                                PrenominaIncidencias.objects.filter(pk=id).delete()
                                
                messages.success(request,"Se han eliminado incidencias de la prenomina")         
                return redirect(request.META.get('HTTP_REFERER'))
            
            #es para guardar la autorizacion - enviar la prenomina para revisión
            if 'enviar_prenomina' in request.POST:
                revisado_rh, created = AutorizarPrenomina.objects.get_or_create(prenomina=prenomina, tipo_perfil=user_filter.tipo)
                revisado_rh.estado =  Estado.objects.get(pk=1) #aprobado
                perfil_rh = Perfil.objects.get(numero_de_trabajador = user_filter.numero_de_trabajador, distrito = user_filter.distrito)
                revisado_rh.perfil=perfil_rh
                revisado_rh.comentario="Revisado por RH"
                revisado_rh.save()
                
                messages.success(request, 'Se ha enviado la prenomina para revisión')  
                return redirect("Prenomina")
            
            if request.method =='POST' and 'economico_pdf' in request.POST:
                fecha_economico = request.POST['economico_pdf']
                fecha_economico = parser.parse(fecha_economico).date()
                solicitud= Solicitud_economicos.objects.get(status=costo.status,fecha=fecha_economico)
                return PdfFormatoEconomicos(request, solicitud)
                #return redirect(request.META.get('HTTP_REFERER'))
            
            if request.method =='POST' and 'vacaciones_pdf' in request.POST:
                fecha_vacaciones = request.POST['vacaciones_pdf']
                fecha_vacaciones = parser.parse(fecha_vacaciones).date()
                solicitud = Solicitud_vacaciones.objects.filter(status=costo.status, fecha_inicio__lte=fecha_vacaciones, fecha_fin__gte=fecha_vacaciones).first()
                return PdfFormatoVacaciones(request, solicitud)
                #return redirect(request.META.get('HTTP_REFERER'))
            
        else:
            
            #EJEUCUTA LOS QUERIES FESTIVOS, ECONOMICOS, FESTIVOS, RANGOS Y GUARDA LOS DATOS
            catorcena = obtener_catorcena()
            #obtener los queries para su posterior llenado
            festivos = TablaFestivos.objects.filter(dia_festivo__range=[catorcena_actual.fecha_inicial, catorcena_actual.fecha_final]) #festivos en la catorcena actual
            economicos = Economicos_dia_tomado.objects.filter(prenomina__status=prenomina.empleado.status, fecha__range=[catorcena_actual.fecha_inicial, catorcena_actual.fecha_final], complete = False)
            vacaciones = Vacaciones_dias_tomados.objects.filter(prenomina__status=prenomina.empleado.status,fecha_inicio__lte=catorcena.fecha_final,fecha_fin__gte=catorcena.fecha_inicial)
            incidencias_rango = IncidenciaRango.objects.filter(empleado_id=prenomina.empleado_id,fecha_inicio__lte=catorcena.fecha_final,fecha_fin__gte=catorcena.fecha_inicial)
            
            #se ejecuta el rango de incidencia en primer lugar - Siempre se tendra una incidencia para la siguiente catorcena
            if incidencias_rango:
                for incidencia_rango in incidencias_rango:
                    fecha_actual = incidencia_rango.fecha_fin
                    fecha_fin = incidencia_rango.fecha_fin
                                
                fecha_actual = max(incidencia_rango.fecha_inicio,prenomina.catorcena.fecha_inicial) #punto de inicio
                fecha_fin = min(incidencia_rango.fecha_fin, prenomina.catorcena.fecha_final)#toma la fecha mas chica entre las dos fechas
                
                #empieza la extracion del rango de incidencia para ubicarlar una por una en el modelo PrenominaIncidencias
                while fecha_actual <= fecha_fin:
                    incidencia = incidencia_rango.incidencia_id
                    comentario = incidencia_rango.comentario
                    soporte = incidencia_rango.soporte
                    
                    #Registra ya sea domingo o descanso
                    if fecha_actual.weekday() == (incidencia_rango.dia_inhabil_id - 1): 
                        if (incidencia_rango.dia_inhabil_id - 1) == 6:# se resta 1 para obtener el dia domingo
                            incidencia = 5 #domingo
                            comentario = None
                            soporte = None
                        else:
                            incidencia = 2 #descanso
                            comentario = None
                            soporte = None
                    
                    #actuliza o crea - es para que solo se creen las necesearias
                    registro_prenomina, creado = PrenominaIncidencias.objects.update_or_create(
                    prenomina=prenomina,
                        fecha=fecha_actual,
                        defaults={
                            'comentario': comentario, 
                            'soporte': soporte,
                            'incidencia_id': incidencia,
                            'incidencia_rango':incidencia_rango,                        
                        }
                    )
                    fecha_actual += timedelta(days=1)
            
            #para obtenter los festivos          
            for festivo in festivos:
                registro, created = PrenominaIncidencias.objects.update_or_create(
                    prenomina_id=prenomina.id,
                    fecha=festivo.dia_festivo,
                    defaults={
                        'incidencia_id': 13 #festivo
                    }
                )
            
            #para obtener los economicos
            for economico in economicos:
                registro, created = PrenominaIncidencias.objects.update_or_create(
                    prenomina_id=prenomina.id,
                    fecha=economico.fecha,
                    defaults={
                        'incidencia_id': 14 # economico
                    }
                )

            #para obtener las vacaciones
            for vacacion in vacaciones:
                    #se ajusta la fecha de acuerdo a la catorcena
                    fecha_inicio = max(vacacion.fecha_inicio, prenomina.catorcena.fecha_inicial)
                    fecha_fin = min(vacacion.fecha_fin, prenomina.catorcena.fecha_final)
                    #se considera el dia inhabil (descanso)       
                    dia_inhabil = vacacion.dia_inhabil_id
                    
                    fecha = fecha_inicio
                    incidencia = 0
                    #sacar las fechas
                    while fecha_inicio <= fecha_fin:
                        if fecha_inicio <= fecha <= fecha_fin:
                            incidencia = 15 # vacacion
                            #verifica si es domingo o descanso
                            if fecha_inicio.weekday() == (dia_inhabil - 1): 
                                if (dia_inhabil - 1) == 6:# se resta 1 para obtener el dia domingo
                                    incidencia = 5 #domingo
                                else:
                                    incidencia = 2 #descanso
                            elif fecha_inicio in [festivo.dia_festivo for festivo in festivos]:
                                incidencia = 13 #festivo:
                        #registra la incidencia
                        registro, created = PrenominaIncidencias.objects.update_or_create(
                            prenomina_id=prenomina.id,
                            fecha=fecha,
                            defaults={
                             'incidencia_id': incidencia
                            }
                        )  
                           
                        #se agregar un dia para realizar el recorrido de la fecha          
                        fecha_inicio += timedelta(days=1)
                        fecha +=   timedelta(days=1)

            #PREPARA LOS FORMULARIOS PARA SER MOSTRADOS CON LAS INCIDENCIAS
            fecha_inicial = catorcena_actual.fecha_inicial  # Fecha inicial
            # 5 domingo, 16 asistencia, 6 y 13 domingo calendario
            datos_iniciales = [{'fecha': fecha_inicial + timedelta(days=i),'incidencia':5 if i == 6 or i == 13 else 16} for i in range(14)] # se preparan los 14 forms con su fecha, 12 asistencias, 2 domingos
            #se filtra las incidencias por la prenomina es decir por el empleado
            incidencias = PrenominaIncidencias.objects.filter(prenomina = prenomina)
            
            # Iterar sobre las incidencias y actualizar los datos iniciales si coinciden con la fecha - volcar el query incidencias a los formularios
            for incidencia in incidencias:
                for data in datos_iniciales:
                    if incidencia.fecha == data['fecha']:
                        data['soporte'] = incidencia.soporte
                        data['comentario'] = incidencia.comentario
                        data['incidencia'] = incidencia.incidencia_id
                        data['id'] = incidencia.id  
                        data['id_rango'] = incidencia.incidencia_rango_id
                        
            prenomina_incidencias_form = PrenominaIncidenciasFormSet(initial=datos_iniciales)
            incidencia_rango_form = IncidenciaRangoForm()
            context = {
                'prenomina':prenomina,
                'costo':costo,
                'catorcena_actual':catorcena_actual,
                'autorizacion1':autorizacion1,
                'autorizacion2':autorizacion2,
                'catorcena_actual':catorcena_actual,
                'prenomina_incidencias_form': prenomina_incidencias_form,
                'incidencia_rango_form':incidencia_rango_form
                
            }
            end_time = time.time()  # Registrar el tiempo de finalización
            print(f"Tiempo total de carga de la página: {end_time - start_time} segundos")
            return render(request, 'prenomina/Actualizar_revisar.html',context)
    else:
        return render(request, 'revisar/403.html')

@login_required(login_url='user-login')
def determinar_estado_general(request, ultima_autorizacion):
    if ultima_autorizacion is None:
        return "Sin autorizaciones"

    tipo_perfil = ultima_autorizacion.tipo_perfil.nombre.lower()
    estado_tipo = ultima_autorizacion.estado.tipo.lower()

    if tipo_perfil == 'rh' and estado_tipo == 'aprobado': #Ultimo upd rh y fue aprobado
        return 'Controles técnicos pendiente'              #Solo puede editarlo ct

    if tipo_perfil == 'control tecnico' and estado_tipo == 'aprobado': #Ultimo upd ct y fue aprobado
        return 'Gerente pendiente'                         
    
    if tipo_perfil == 'gerencia' and estado_tipo == 'aprobado': #Ultimo upd gerencia y fue aprobado
        return 'Gerente aprobado (Prenomina aprobada)'

    if tipo_perfil == 'control tecnico' and estado_tipo == 'rechazado': #Ultimo upd ct y fue rechazado
        return 'RH pendiente (rechazado por Controles técnicos)'
    
    if tipo_perfil == 'gerencia' and estado_tipo == 'rechazado': #Ultimo upd gerencia y fue rechazado
        return 'RH pendiente (rechazado por Gerencia)'

    return 'Estado no reconocido'

def PdfFormatoEconomicos(request, solicitud):
    solicitud= Solicitud_economicos.objects.get(id=solicitud.id)
    now = date.today()
    fecha = solicitud.fecha
    periodo = str(fecha.year)
    economico = 0
    if not Economicos.objects.filter(status=solicitud.status):
        economico = 0
    else:
        last_economico = Economicos.objects.filter(status=solicitud.status).last()
        economico = last_economico.dias_disfrutados
    #Para ubicar el dia de regreso en un dia habil (Puede caer en día festivo)
    #if status.regimen.regimen == 'L-V':
    #    inhabil1 = 6
    #    inhabil2 = 7
    #elif status.regimen.regimen == 'L-S':
    #    inhabil1 = 7
    #    inhabil2 = None
    regreso = fecha + timedelta(days=1)
    #if regreso.isoweekday() == inhabil1:
    #    regreso = regreso + timedelta(days=1)
    #if regreso.isoweekday() == inhabil2:
    #    regreso = regreso + timedelta(days=1)


    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    #Colores utilizados
    azul = Color(0.16015625,0.5,0.72265625)
    rojo = Color(0.59375, 0.05859375, 0.05859375)

    c.setFillColor(black)
    c.setLineWidth(.2)
    c.setFont('Helvetica-Bold',16)
    c.drawCentredString(305,765,'GRUPO VORCAB SA DE CV')
    c.setFont('Helvetica-Bold',11)
    c.drawCentredString(305,750,'SOLICITUD DE DIA ECONOMICO')
    if solicitud.autorizar == False:
        c.setFillColor(rojo)
        c.setFont('Helvetica-Bold',16)
        c.drawCentredString(305,725,'SOLICITUD NO AUTORIZADA')
    c.setFillColor(black)
    c.setFont('Helvetica-Bold',11)
    c.drawString(40,690,'NOMBRE:')
    c.line(95,688,325,688)
    espacio = ' '
    nombre_completo = str(solicitud.status.perfil.nombres + espacio + solicitud.status.perfil.apellidos)
    c.drawString(100,690,nombre_completo)
    c.drawString(40,670,'PUESTO:')
    c.line(95,668,325,668)
    c.drawString(100,670,solicitud.status.puesto.puesto)
    c.drawString(335,670,'TELEFONO PARTICULAR:')
    c.line(475,668,580,668)
    c.drawString(485,670,solicitud.status.telefono)
    c.drawString(40,620,'FECHA DE PLANTA:')
    if solicitud.status.fecha_planta != None:
        dia = str(solicitud.status.fecha_planta.day)
        mes = str(solicitud.status.fecha_planta.month)
        año = str(solicitud.status.fecha_planta.year)
    else:
        dia = "NR"
        mes = "NR"
        año = "NR"
    #rect(x, y, alto, ancho, stroke=1, fill=0)
    c.rect(185,600, 150, 50)
    c.line(185,618,335,618)
    c.line(185,638,335,638)
    c.line(230,650,230,600)
    c.line(290,650,290,600)
    c.drawCentredString(210,620,dia)
    c.drawCentredString(260,620,mes)
    c.drawCentredString(310,620,año)
    c.drawString(40,600,'FECHA DE SOLICITUD:')
    c.drawCentredString(210,605,str(now.day))
    c.drawCentredString(260,605,str(now.month))
    c.drawCentredString(310,605,str(now.year))
    c.drawString(200,640,'DIA')
    c.drawString(250,640,'MES')
    c.drawString(300,640,'AÑO')
    c.drawString(400,600,'FIRMA DEL SOLICITANTE')
    c.rect(390,598, 155, 50)
    c.line(390,610,545,610)
    c.drawString(40,540,'PERIODO CORRESPONDIENTE:')
    c.drawCentredString(450,540, periodo)
    c.rect(35,538, 255, 12)
    c.rect(360,538, 190, 12)
    c.drawCentredString(385,520,'1')
    c.drawCentredString(435,520,'2')
    c.drawCentredString(485,520,'3')

    c.drawString(40,500,'NO. DE DIA ECONOMICO:')
    c.rect(35,498, 175, 12)
    c.rect(360,498, 150, 12)
    c.line(410,510,410,498)
    c.line(460,510,460,498)
    c.setFillColorRGB(0.8, 0.8, 0.8)  # Color de relleno
    if economico == 1:
        c.rect(360,498, 50, 12, stroke = 1, fill = 1)
    elif economico == 2:
        c.rect(410,498, 50, 12, stroke = 1, fill = 1)
    elif economico == 3:
        c.rect(460,498, 50, 12, stroke = 1, fill = 1)
    c.setFillColor(black)
    c.drawString(40,480,'CON GOCE DE SUELDO:')
    c.rect(35,478, 140, 12)
    c.drawString(380,480,'SI')
    c.rect(360,478, 50, 12)
    c.drawString(425,480,'NO')
    c.rect(410,478, 50, 12)
    c.drawString(40,460,'FECHA QUE DESEA SALIR DEL PERMISO:')
    c.drawCentredString(450,460,str(fecha))
    c.rect(35,458, 250, 12)
    c.rect(360,458, 190, 12)
    c.drawString(40,440,'FECHA DE REGRESO A LABORES:')
    c.drawCentredString(450,440,str(regreso))
    c.rect(35,438, 195, 12)
    c.rect(360,438, 190, 12)
    #c.drawCentredString(305,370,'OBSERVACIONES')
    text = solicitud.comentario
    x = 40
    y = 385
    c.setFillColor(black)
    c.setFont('Helvetica-Bold',12)
    c.drawCentredString(310, y - 15, 'OBSERVACIONES')
    c.setFont('Helvetica', 9)
    lines = textwrap.wrap(text, width=100)
    for line in lines:
        c.drawString(x + 10, y - 30, line)
        y -= 25
    c.rect(40,368, 530, 12)
    c.rect(40,300, 530, 68)
    c.drawCentredString(170,125,'FIRMA GERENCIA')
    c.rect(70,123, 200, 12)
    c.rect(70,135, 200, 50)
    c.drawCentredString(440,125,'FIRMA DE JEFE INMEDIATO')
    c.rect(330,123, 210, 12)
    c.rect(330,135, 210, 50)
    c.save()
    c.showPage()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='Formato_Economico.pdf')

@login_required(login_url='user-login')
def PdfFormatoVacaciones(request, solicitud):
    solicitud= Solicitud_vacaciones.objects.get(id=solicitud.id)
    inicio = solicitud.fecha_inicio
    fin = solicitud.fecha_fin
    dia_inhabil = solicitud.dia_inhabil
    ######
    tabla_festivos = TablaFestivos.objects.all()
    delta = timedelta(days=1)
    day_count = (fin - inicio + delta ).days
    cuenta = day_count
    inhabil = dia_inhabil.numero
    for fecha in (inicio + timedelta(n) for n in range(day_count)):
        if fecha.isoweekday() == inhabil:
            cuenta -= 1
        else:
            for dia in tabla_festivos:
                if fecha == dia.dia_festivo:
                    cuenta -= 1
    diferencia = str(cuenta)
    #Para ubicar el dia de regreso en un dia habil (Puede caer en día festivo)
    fin = fin + timedelta(days=1)
    if fin.isoweekday() == inhabil:
        fin = fin + timedelta(days=1)
    now = date.today()
    año1 = str(inicio.year)
    año2= str(fin.year)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    #Colores utilizados
    azul = Color(0.16015625,0.5,0.72265625)
    rojo = Color(0.59375, 0.05859375, 0.05859375)

    c.setFillColor(azul)
    c.setLineWidth(.2)
    c.setFont('Helvetica-Bold',16)
    c.drawCentredString(305,765,'GRUPO VORCAB SA DE CV')
    c.drawCentredString(305,750,'SOLICITUD DE VACACIONES')
    c.drawInlineImage('static/images/vordcab.png',50,720, 4 * cm, 2 * cm) #Imagen Savia
    if solicitud.autorizar == False:
        c.setFillColor(rojo)
        c.setFont('Helvetica-Bold',16)
        c.drawCentredString(305,725,'SOLICITUD NO AUTORIZADA')
    c.setFillColor(black)
    c.setFont('Helvetica-Bold',11)
    c.drawString(40,690,'NOMBRE:')
    c.line(95,688,325,688)
    espacio = ' '
    nombre_completo = str(solicitud.status.perfil.nombres + espacio + solicitud.status.perfil.apellidos)
    c.drawString(100,690,nombre_completo)
    c.drawString(40,670,'PUESTO:')
    c.line(95,668,325,668)
    c.drawString(100,670,solicitud.status.puesto.puesto)

    c.drawString(335,670,'TELEFONO PARTICULAR:')
    c.line(475,668,580,668)
    c.drawString(485,670,solicitud.status.telefono)

    if cuenta < 3:
        altura=200
        margen=20
        c.drawCentredString(305,502,'OBSERVACIONES')
        if solicitud.comentario_rh:
            c.drawString(55,490,solicitud.comentario_rh)
        else:
            c.drawString(55,490,'ninguna')
        c.rect(50,500, 510, 12)
        c.rect(50,435, 510, 65)
    else:
        altura=0
        margen=0
    c.drawString(40,620-margen,'FECHA DE PLANTA:')
    if solicitud.status.fecha_planta != None:
        dia = str(solicitud.status.fecha_planta.day)
        mes = str(solicitud.status.fecha_planta.month)
        año = str(solicitud.status.fecha_planta.year)
    else:
        dia = "NR"
        mes = "NR"
        año = "NR"

    c.rect(185,598-margen, 150, 55)
    c.line(185,618-margen,335,618-margen)
    c.line(185,638-margen,335,638-margen)
    c.line(230,650-margen,230,598-margen)
    c.line(290,650-margen,290,598-margen)
    c.drawCentredString(210,620-margen,dia)
    c.drawCentredString(260,620-margen,mes)
    c.drawCentredString(310,620-margen,año)
    c.drawString(40,600-margen,'FECHA DE SOLICITUD:')
    c.drawCentredString(210,600-margen,str(now.day))
    c.drawCentredString(260,600-margen,str(now.month))
    c.drawCentredString(310,600-margen,str(now.year))
    c.drawString(200,640-margen,'DIA')
    c.drawString(250,640-margen,'MES')
    c.drawString(300,640-margen,'AÑO')
    c.drawString(400,600-margen,'FIRMA DEL SOLICITANTE')
    c.rect(390,598-margen, 155, 55)
    c.line(390,610-margen,545,610-margen)

    c.drawString(40,560-altura,'PERIODO VACACIONAL CORRESPONDIENTE:')
    c.drawCentredString(425,560-altura, año1)
    c.drawCentredString(450,560-altura, '/')
    c.drawCentredString(475,560-altura, año2)
    c.rect(35,558-altura, 255, 12)
    c.rect(360,558-altura, 190, 12)
    #form = VacacionesFormato(request.POST,)
    c.drawString(40,540-altura,'NO. DE DIAS DE VACACIONES:')
    c.drawCentredString(450,540-altura,diferencia)
    c.rect(35,538-altura, 175, 12)
    c.rect(360,538-altura, 190, 12)
    c.drawString(40,520-altura,'CON GOCE DE SUELDO:')
    c.rect(35,518-altura, 140, 12)
    c.drawString(380,520-altura,'SI')
    c.rect(360,518-altura, 50, 12)
    c.drawString(425,520-altura,'NO')
    c.rect(410,518-altura, 50, 12)
    c.drawString(40,500-altura,'FECHA QUE DESEA SALIR DE VACACIONES:')
    c.drawCentredString(450,500-altura,str(inicio))
    c.rect(35,498-altura, 250, 12)
    c.rect(360,498-altura, 190, 12)
    c.drawString(40,480-altura,'FECHA DE REGRESO A LABORES:')
    c.drawCentredString(450,480-altura,str(fin))
    c.rect(35,478-altura, 195, 12)
    c.rect(360,478-altura, 190, 12)
    if cuenta >= 3: ########### Para formatos largos
        c.drawCentredString(300,440,'Entrega-Recepción')
        c.setFont('Helvetica',11)
        c.drawString(40,400,'DATOS DE QUIEN RECIBE:')
        c.drawString(40,380,'Nombre:')
        if solicitud.recibe_nombre:
            c.drawString(100,380,solicitud.recibe_nombre)
        c.line(90,378,375,378)
        c.drawString(385,380,'Area:')
        if solicitud.recibe_area:
            c.drawString(435,380,solicitud.recibe_area)
        c.line(420,378,560,378)
        c.drawString(40,360,'Puesto:')
        if solicitud.recibe_puesto:
            c.drawString(100,360,solicitud.recibe_puesto)
        c.line(90,358,375,358)
        c.drawString(40,340,'Sector:')
        if solicitud.recibe_sector:
            c.drawString(100,340,solicitud.recibe_sector)
        c.line(90,338,375,338)
        c.setFont('Helvetica-Bold',14)
        c.drawString(40,300,'SITUACIÓN DE TRABAJOS ENCOMENDADOS:')
        c.setFillColor(black)
        c.setFont('Helvetica',11)

        # Estilo de párrafo para los datos en la tabla
        styleSheet = getSampleStyleSheet()
        paragraphStyle = styleSheet['Normal']
        paragraphStyle.fontSize = 8
        #Tabla y altura guia
        high = 130
        trabajos = Trabajos_encomendados.objects.filter(solicitud_vacaciones__id=solicitud.id)
        data = []
        data.append(['No.', 'DENOMINACIÓN ASUNTO', 'ESTADO'])

        numero = 1  # Inicializar el número

        for index, trabajo in enumerate(trabajos, start=1):
            trabajo_data = []
            for i in range(1, 11):
                asunto = getattr(trabajo, f'asunto{i}', '')
                estado = getattr(trabajo, f'estado{i}', '')
                trabajo_data.append((numero, asunto, estado))
                numero += 1  # Incrementar el número
            data.extend(trabajo_data)
        high = high - 20

        #Propiedades de la tabla
        width, height = landscape(letter)
        table_style = TableStyle([ #estilos de la tabla
            #ENCABEZADO
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TEXTCOLOR',(0,0),(-1,0), colors.black),
            ('FONTSIZE',(0,0),(-1,0), 12),
            ('BACKGROUND',(0,0),(-1,0), colors.white),
            #CUERPO
            ('TEXTCOLOR',(0,1),(-1,-1), colors.black),
            ('FONTSIZE',(0,1),(-1,-1), 12),
            ('GRID',(0,0),(-1,-1),0.5,colors.grey),
        ])

        # Definir variables para el salto de página
        rows_per_page = 7
        total_rows = len(data) - 1  # Excluye el encabezado
        current_row = 1  # Comenzar desde la primera fila (excluyendo el encabezado)

        # Generar páginas con el contenido restante
        while current_row <= total_rows:
            # Calcular el espacio disponible en la página actual
            available_height = height - 70 - 20  # Ajustar según el espaciado

            # Calcular cuántas filas caben en la página actual
            if current_row == 1:
                rows_on_page = min(rows_per_page, math.floor((available_height - 20) / 20))  # Para la primera página
            else:
                rows_on_page = min(20, math.floor((available_height - 20) / 20))  # Para las páginas restantes

            # Obtener los datos para la página actual
            end_row = int(current_row + rows_on_page) if current_row + rows_on_page <= total_rows else total_rows + 1
            page_data = data[current_row:end_row]

            # Reemplazar valores None con un espacio en blanco
            page_data = [[cell if cell is not None else " " for cell in row] for row in page_data]

            # Calcular la altura para dibujar la tabla
            table_height = len(page_data) * 20

            # Calcular la posición vertical para la tabla
            if current_row == 1:
                # Ajustar el margen superior para la primera tabla
                table_y = height - 130 - table_height - 275  # Usar la altura específica para la primera tabla
            else:
                # Calcular el margen desde la parte superior de la página
                margin_top = 40
                table_y = height - table_height - margin_top

            # Dentro del bucle para crear la tabla de cada página
            table_data = []
            for row in page_data:
                table_row = []
                for cell_data in row:
                    if isinstance(cell_data, str) and len(cell_data) > 30:
                        # Aplicar estilo CSS para dividir palabras largas
                        cell_data = cell_data.replace(' ', '<br/>')
                        cell_data = f'<font size="12">{cell_data}</font>'
                        cell = Paragraph(cell_data, paragraphStyle)
                    else:
                        cell = cell_data
                    table_row.append(cell)
                table_data.append(table_row)

            # Crear la tabla para la página actual
            table = Table([data[0]] + table_data, colWidths=[1.5 * cm, 8 * cm, 10 * cm], repeatRows=1)
            table.setStyle(table_style)

            # Dibujar la tabla en la página actual
            table.wrapOn(c, width, height)
            table.drawOn(c, 25, table_y)

            # Avanzar al siguiente conjunto de filas
            current_row += rows_on_page

            # Cambiar la cantidad de filas por página después de la primera página
            if current_row == 1:
                rows_per_page = 20

            # Agregar una nueva página si quedan más filas por dibujar
            if current_row <= total_rows:
                c.showPage()
        c.showPage()
        c.setFont('Helvetica-Bold',12)
        #Parrafo con salto de linea automatica si el texto es muy largo
        text = " "
        if solicitud.informacion_adicional:
            text = solicitud.informacion_adicional
        x = 40
        y = 750
        c.setFillColor(black)
        c.setFont('Helvetica', 12)
        c.drawString(x + 5, y - 15, 'INFORMACIÓN ADICIONAL:')
        c.setFont('Helvetica', 9)
        lines = textwrap.wrap(text, width=100)
        for line in lines:
            c.drawString(x + 10, y - 35, line)
            y -= 15

        # Estilo de párrafo para los comentarios
        styleSheet = getSampleStyleSheet()
        commentStyle = styleSheet['Normal']
        commentStyle.fontSize = 8

        def format_comment(comment):
            if comment is None:
                return ""
            return Paragraph(comment, commentStyle)

        # Datos y ajustes de la tabla
        data2 = []
        high = 465
        data2.append(['No.', 'TEMAS', 'COMENTARIO'])
        data2.append(["1", "Información sobre personal a su cargo", format_comment(solicitud.temas.comentario1)])
        data2.append(["2", "Documentos", format_comment(solicitud.temas.comentario2)])
        data2.append(["3", Paragraph("Arqueo de caja o cuenta bancaria a su cargo (cuando aplique)"), format_comment(solicitud.temas.comentario3)])
        data2.append(["4", "Proyectos pendientes", format_comment(solicitud.temas.comentario4)])
        data2.append(["5", "Estado de las operaciones a su cargo", format_comment(solicitud.temas.comentario5)])
        data2.append(["6", "Deudas con la empresa", format_comment(solicitud.temas.comentario6)])
        data2.append(["7", "Saldos por comprobar a contabilidad", format_comment(solicitud.temas.comentario7)])
        data2.append(["8", "Activos asignados", format_comment(solicitud.temas.comentario8)])
        data2.append(["9", "Otros", format_comment(solicitud.temas.comentario9)])

        table = Table(data2, colWidths=[1.5 * cm, 8 * cm, 11 * cm,], repeatRows=1)
        table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TEXTCOLOR',(0,0),(-1,0), colors.black),
            ('FONTSIZE',(0,0),(-1,0), 13),
            ('BACKGROUND',(0,0),(-1,0), colors.white),
            ('GRID',(0,0),(-1,-1),0.5,colors.grey),
        ]))

        # Dibujar la tabla en el lienzo
        table.wrapOn(c, width, height)
        table.drawOn(c, 25, high)

        #c.drawString(40,375,'ANEXOS:')
        text = " "
        if solicitud.anexos:
            text = solicitud.anexos
        x = 40
        y = 380
        c.setFillColor(black)
        c.setFont('Helvetica', 12)
        c.drawString(x + 5, y - 15, 'Anexos:')
        c.setFont('Helvetica', 9)
        lines = textwrap.wrap(text, width=100)
        for line in lines:
            c.drawString(x + 10, y - 30, line)
            y -= 25
        c.line(40,345,570,345)
        c.line(40,320,570,320)
        c.line(40,293,570,293)
        c.line(40,270,570,270)
        c.drawCentredString(200,170,'ENTREGUE (NOMBRE Y FIRMA)')
        c.drawCentredString(200,190,nombre_completo)
        c.line(105,185,295,185)
        c.drawCentredString(400,170,'RECIBI (NOMBRE Y FIRMA)')
        c.drawCentredString(400,190,solicitud.recibe_nombre)
        c.line(320,185,480,185)

    c.drawCentredString(200,70,'FIRMA DE GERENCIA')
    c.rect(120,68, 160, 70)
    c.line(120,80,280,80)
    c.drawCentredString(400,70,'FIRMA DE JEFE INMEDIATO')
    c.rect(300,68, 195, 70)
    c.line(300,80,495,80)
    c.save()
    c.showPage()
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='Formato_Vacaciones.pdf')

@login_required(login_url='user-login')
def obtener_fechas_con_incidencias(request, prenomina, catorcena_actual):
    # Crear lista de fechas entre fecha_inicial y fecha_final de la catorcena
    dias_entre_fechas = [(catorcena_actual.fecha_inicial + timedelta(days=i)) for i in range((catorcena_actual.fecha_final - catorcena_actual.fecha_inicial).days + 1)]

    # Obtener todas las incidencias en una sola consulta
    todas_incidencias = PrenominaIncidencias.objects.filter(
        prenomina__empleado_id=prenomina.empleado_id,
        fecha__range=(catorcena_actual.fecha_inicial, catorcena_actual.fecha_final)
    ).values('fecha', 'incidencia__id')

    # Mapeo de id de incidencia a su etiqueta
    id_to_etiqueta = {
        1: "retardos",
        2: "descanso",
        3: "faltas",
        4: "comision",
        5: "domingo",
        6: "dia_extra",
        7: "castigos",
        8: "permisos_sin_goce",
        9: "permisos_con_goce",
        10: "incapacidad_enfermedad_general",
        11: "incapacidad_riesgo_laboral",
        12: "incapacidad_maternidad",
        13: "festivo",
        14: "economicos",
        15: "vacaciones"
    }

    # Crear un diccionario para almacenar las fechas con su incidencia
    fecha_a_etiqueta = {fecha: "asistencia" for fecha in dias_entre_fechas}

    # Asignar etiquetas a las fechas según las incidencias
    for incidencia in todas_incidencias:
        fecha = incidencia['fecha']
        incidencia_id = incidencia['incidencia__id']
        etiqueta = id_to_etiqueta.get(incidencia_id, "asistencia")
        fecha_a_etiqueta[fecha] = etiqueta

    # Crear la lista final de fechas con sus etiquetas
    fechas_con_etiquetas = [(fecha, etiqueta) for fecha, etiqueta in fecha_a_etiqueta.items()]

    return fechas_con_etiquetas

@login_required(login_url='user-login')
def Excel_estado_prenomina_formato(request,prenominas, user_filter):
    from datetime import datetime
    
    response= HttpResponse(content_type = "application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename = Reporte_prenomina_días_' + str(datetime.now())+'.xlsx'
    wb = Workbook()
    ws = wb.create_sheet(title='Reporte')
    #Comenzar en la fila 1
    row_num = 3

    #Create heading style and adding to workbook | Crear el estilo del encabezado y agregarlo al Workbook
    head_style = NamedStyle(name = "head_style")
    head_style.font = Font(name = 'Arial', color = '00FFFFFF', bold = True, size = 11)
    head_style.fill = PatternFill("solid", fgColor = '00003366')
    wb.add_named_style(head_style)
    #Create body style and adding to workbook
    body_style = NamedStyle(name = "body_style")
    body_style.font = Font(name ='Calibri', size = 11)
    wb.add_named_style(body_style)
    #Create messages style and adding to workbook
    messages_style = NamedStyle(name = "mensajes_style")
    messages_style.font = Font(name="Arial Narrow", size = 11)
    wb.add_named_style(messages_style)
    #Create date style and adding to workbook
    date_style = NamedStyle(name='date_style', number_format='DD/MM/YYYY')
    date_style.font = Font(name ='Calibri', size = 11)
    wb.add_named_style(date_style)
    money_style = NamedStyle(name='money_style', number_format='$ #,##0.00')
    money_style.font = Font(name ='Calibri', size = 11)
    bold_money_style = NamedStyle(name='bold_money_style', number_format='$#,##0.00', font=Font(bold=True))
    wb.add_named_style(money_style)
    money_resumen_style = NamedStyle(name='money_resumen_style', number_format='$ #,##0.00')
    money_resumen_style.font = Font(name ='Calibri', size = 14, bold = True)
    wb.add_named_style(money_resumen_style)
    dato_style = NamedStyle(name='dato_style',number_format='DD/MM/YYYY')
    dato_style.font = Font(name="Arial Narrow", size = 11)
    ahora = datetime.now()
    #ahora = datetime.now() + timedelta(days=10)
    # todas las fechas de la catorcena actual
    catorcena_actual = Catorcenas.objects.filter(fecha_inicial__lte=ahora, fecha_final__gte=ahora).first()
    delta = catorcena_actual.fecha_final - catorcena_actual.fecha_inicial
    dias_entre_fechas = [catorcena_actual.fecha_inicial + timedelta(days=i) for i in range(delta.days + 1)]
    # Generar los nombres de las columnas de los días
    dias_columnas = [str(fecha.day) for fecha in dias_entre_fechas]
        
    columns = ['No.','NOMBRE DE EMPLEADO','PUESTO','PROYECTO','SUBPROYECTO'] + dias_columnas + ['Salario Catorcenal','Salario Catorcenal',
               'Previsión social', 'Total bonos','Total percepciones','Prestamo infonavit','Fonacot','Total deducciones','Neto a pagar en nomina','Salario','Salario Domingo',]
    
    for col_num in range(len(columns)):
        (ws.cell(row = row_num, column = col_num+1, value=columns[col_num])).style = head_style
        if col_num == 1:
            ws.column_dimensions[get_column_letter(col_num + 1)].width = 50
        if col_num < 4:
            ws.column_dimensions[get_column_letter(col_num + 1)].width = 30
        if col_num == 4:
            ws.column_dimensions[get_column_letter(col_num + 1)].width = 30
        else:
            ws.column_dimensions[get_column_letter(col_num + 1)].width = 15


    columna_max = len(columns)+2
    
    ahora = datetime.now()
    #ahora = datetime.now() + timedelta(days=10)
    
    catorcena_actual = Catorcenas.objects.filter(fecha_inicial__lte=ahora, fecha_final__gte=ahora).first()
    (ws.cell(column = 1, row = 1, value='Reporte Prenomina SAVIA RH')).style = messages_style
    (ws.cell(column = 1, row = 2, value=f'Catorcena: {catorcena_actual.catorcena}: {catorcena_actual.fecha_inicial.strftime("%d/%m/%Y")} - {catorcena_actual.fecha_final.strftime("%d/%m/%Y")}')).style = dato_style
    ws.column_dimensions[get_column_letter(columna_max)].width = 50
    ws.column_dimensions[get_column_letter(columna_max + 1)].width = 50

    rows = []

    sub_salario_catorcenal_costo = Decimal(0.00) #Valor de referencia del costo
    sub_salario_catorcenal = Decimal(0.00)
    sub_apoyo_pasajes = Decimal(0.00)
    sub_total_bonos = Decimal(0.00)
    sub_total_percepciones = Decimal(0.00)
    sub_prestamo_infonavit = Decimal(0.00)
    sub_prestamo_fonacot = Decimal(0.00)
    sub_total_deducciones = Decimal(0.00)
    sub_pagar_nomina = Decimal(0.00)
        
    for prenomina in prenominas:
        #datos para obtener los calculos de la prenomina dependiendo el empleado
        salario_catorcenal_costo = (prenomina.empleado.status.costo.neto_catorcenal_sin_deducciones)
        
        salario = Decimal(prenomina.empleado.status.costo.neto_catorcenal_sin_deducciones) / 14
        neto_catorcenal =  prenomina.empleado.status.costo.neto_catorcenal_sin_deducciones
        apoyo_pasajes = prenomina.empleado.status.costo.apoyo_de_pasajes
        infonavit = prenomina.empleado.status.costo.amortizacion_infonavit
        fonacot = prenomina.empleado.status.costo.fonacot 
        
        #Fecha para obtener los bonos agregando la hora y la fecha de acuerdo a la catorcena
        fecha_inicial = datetime.combine(catorcena_actual.fecha_inicial, datetime.min.time()) + timedelta(hours=00, minutes=00,seconds=00)
        fecha_final = datetime.combine(catorcena_actual.fecha_final, datetime.min.time()) + timedelta(hours=23, minutes=59,seconds=59)
        
        total_bonos = BonoSolicitado.objects.filter(
            trabajador_id=prenomina.empleado.status.perfil.id,
            solicitud__fecha_autorizacion__isnull=False,
            solicitud__fecha_autorizacion__range=(fecha_inicial, fecha_final)
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        print("Total Bonos:", total_bonos)
           
        #calculo del infonavit
        if infonavit == 0:
            prestamo_infonavit = Decimal(0.00)
        else:
            prestamo_infonavit = Decimal((infonavit / Decimal(30.4) ) * 14 )
       
        #calculo del fonacot
        if fonacot == 0:
            prestamo_fonacot = Decimal(0.00)
        else:
            #Se haya la catorcena actual, y cuenta cuantas catorcenas le corresponden al mes actual
            primer_dia_mes = datetime(datetime.now().year, datetime.now().month, 1).date()
            ultimo_dia_mes = datetime(datetime.now().year, datetime.now().month,
                                    calendar.monthrange(datetime.now().year, datetime.now().month)[1]).date()
            numero_catorcenas =  Catorcenas.objects.filter(fecha_final__range=(primer_dia_mes,ultimo_dia_mes)).count()
            prestamo_fonacot = prestamo_fonacot / numero_catorcenas
            
        #Contar las incidencias        
        retardos, descansos, faltas, comisiones, domingos, dia_extra, castigos, permisos_sin_goce, permisos_con_goce, incapacidad_riesgo_laboral, incapacidad_maternidad, festivos, economicos, vacaciones, incapacidad_enfermedad_general= calcular_incidencias(request, prenomina, catorcena_actual)

        
        #numero de catorena
        catorcena_num = catorcena_actual.catorcena 
        
        incidencias = 0
        incidencias_retardos = 0
        
        if faltas > 0:
            incidencias = incidencias + faltas
            print("Faltas: ", faltas)
            
        if retardos > 0:
            incidencias_retardos = retardos // 3 #3 retardos se decuenta 1 dia
            
        if castigos > 0:
            incidencias = incidencias + castigos
            print("Castigos incidencias contadas", castigos)
        
        if permisos_sin_goce  > 0:
            incidencias = incidencias + permisos_sin_goce
        
        pago_doble = 0  
        if dia_extra > 0:
            pago_doble = Decimal(dia_extra * salario)
        
        incapacidad = str("")   
        incidencias_incapacidades = 0 #Modificar
        incidencias_incapacidades_pasajes = 0          
        incapacidades = 0         
        cantidad_dias_vacacion = 0
        #calculo de la prenomina - regla de tres   
        dias_de_pago = 12
        dias_laborados = dias_de_pago - (incidencias + incidencias_retardos + incidencias_incapacidades)
        proporcion_septimos_dias = Decimal((dias_laborados * 2) / 12)
        proporcion_laborados = proporcion_septimos_dias + dias_laborados
        salario_catorcenal = (proporcion_laborados * salario) + pago_doble
        
        print("las incidencias incapacidades", incidencias_incapacidades)
        if incidencias_incapacidades_pasajes > 0:
            apoyo_pasajes = (apoyo_pasajes / 12 * (12 - (incidencias + incidencias_incapacidades_pasajes))) #12 son los dias trabajados
            print("Aqui es donde se ejecuta el codigo")
        else:
            apoyo_pasajes = (apoyo_pasajes / 12 * (12 - (incidencias))) #12 son los dias trabajados
            print("Aqui no se deberia ejecutar el codigo")
        
        print("apoyos pasajes: ", apoyo_pasajes)
        print("total: ", salario_catorcenal)
        print("pagar nomina: ", apoyo_pasajes + salario_catorcenal)
        
        total_percepciones = salario_catorcenal + apoyo_pasajes + total_bonos
        total_deducciones = prestamo_infonavit + prestamo_fonacot
        pagar_nomina = total_percepciones - total_deducciones
        
        if retardos == 0: 
            retardos = ''
        
        if castigos == 0:
            castigos = ''
            
        if permisos_con_goce == 0:
            permisos_con_goce = ''
            
        if permisos_sin_goce == 0:
            permisos_sin_goce = ''
            
        if descansos == 0:
            descansos = ''

        if dia_extra == 0:
            dia_extra = ''
                    
        if incapacidades == 0:
            incapacidades = ''
        
        if faltas == 0:
            faltas = ''
        
        if comisiones == 0:
            comisiones = ''
            
        if domingos == 0:
            domingos = ''
            
        if festivos == 0:
            festivos = ''
            
        if economicos == 0:
            economicos = ''
            
        if cantidad_dias_vacacion == 0:
            cantidad_dias_vacacion = ''
    abreviaciones = {
        "economicos": "D/E",
        "castigos": "CAS",
        "retardos": "R",
        "vacaciones": "V",
        "comision": "C",
        "faltas": "F",
        "permisos_con_goce": "PGS",
        "festivo": "FE",
        "incapacidades": "I",
        "permisos_sin_goce": "PSS",
        "descanso": "DEZ",
        "asistencia": "x",
        "domingo": "D",
    }
    abreviaciones_colores_cortas = {
        "D/E": "FF92d050",    # Verde claro
        "CAS": "FF948a54",    # Marrón
        "R": "FFe26b0a",      # Naranja
        "V": "FF00b0f0",      # Azul claro
        "C": "FF538dd5",      # Azul
        "F": "FFFF0000",      # Rojo
        "PGS": "FFfcd5b4",    # Beige
        "FE": "FFb1a0c7",     # Púrpura claro
        "I": "FF963634",      # Rojo oscuro
        "PSS": "FFc00000",    # Rojo oscuro
        "DEZ": "FF00b050",    # Verde
        "x": "FFFFFF",         # Blanco
        "D": "FFFF00"         # Amarillo
    }
    rows = []
    for prenomina in prenominas:
        fechas_con_etiquetas = obtener_fechas_con_incidencias(request, prenomina, catorcena_actual)
        estados_por_dia = [abreviaciones.get(estado, estado) for _, estado in fechas_con_etiquetas]
        row = (
            prenomina.empleado.status.perfil.numero_de_trabajador,
            prenomina.empleado.status.perfil.nombres + ' ' + prenomina.empleado.status.perfil.apellidos,
            prenomina.empleado.status.puesto.puesto,
            prenomina.empleado.status.perfil.proyecto.proyecto,
            prenomina.empleado.status.perfil.subproyecto.subproyecto,
            *estados_por_dia,  # Desempaquetar estados_por_dia aquí
            salario_catorcenal_costo,
            salario_catorcenal,
            apoyo_pasajes,  # Prevision social pasajes
            total_bonos,
            total_percepciones,
            prestamo_infonavit,
            prestamo_fonacot,
            total_deducciones,
            pagar_nomina,
            salario,
            ((proporcion_septimos_dias * salario) / 2)
        )
        rows.append(row)
        
        sub_salario_catorcenal_costo = sub_salario_catorcenal_costo + salario_catorcenal_costo
        sub_salario_catorcenal = sub_salario_catorcenal + salario_catorcenal
        sub_apoyo_pasajes = sub_apoyo_pasajes + apoyo_pasajes
        sub_total_bonos = sub_total_bonos + total_bonos
        sub_total_percepciones = sub_total_percepciones + total_percepciones
        sub_prestamo_infonavit = sub_prestamo_infonavit + prestamo_infonavit
        sub_prestamo_fonacot = sub_prestamo_fonacot + prestamo_fonacot
        sub_total_deducciones = sub_total_deducciones + total_deducciones
        sub_pagar_nomina = sub_pagar_nomina + pagar_nomina
        
        
                 
    # Ahora puedes usar la lista rows como lo estás haciendo actualmente en tu código
    for row_num, row in enumerate(rows, start=4):
        for col_num, value in enumerate(row, start=1):
            if col_num < 4:
                ws.cell(row=row_num, column=col_num, value=value).style = body_style
            elif col_num == 5:
                ws.cell(row=row_num, column=col_num, value=value).style = date_style
            elif 5 < col_num < 24:
                ws.cell(row=row_num, column=col_num, value=value).style = body_style
                # Verificar si el valor está en la lista de abreviaciones
                if value in abreviaciones_colores_cortas:
                    color_hex = abreviaciones_colores_cortas[value]
                    fill = PatternFill(start_color=color_hex, end_color=color_hex, fill_type="solid")
                    ws.cell(row=row_num, column=col_num).fill = fill
            elif col_num >= 24:
                ws.cell(row=row_num, column=col_num, value=value).style = money_style
            else:
                ws.cell(row=row_num, column=col_num, value=value).style = body_style

    add_last_row = ['Total','','','','','','','','','','','','','','','','','','',
                    sub_salario_catorcenal_costo,
                    sub_salario_catorcenal,
                    sub_apoyo_pasajes,
                    sub_total_bonos,
                    sub_total_percepciones,
                    sub_prestamo_infonavit,
                    sub_prestamo_fonacot,
                    sub_total_deducciones,
                    sub_pagar_nomina
                    ]
    ws.append(add_last_row) 

    # Agregar las abreviaciones como una tabla de dos columnas
    for key, value in abreviaciones.items():
        ws.append([key, value])

    # Aplicar el estilo a cada celda de la tabla de abreviaciones cortas con colores de fondo
    for row_num, row in enumerate(ws.iter_rows(min_row=ws.max_row - len(abreviaciones) + 1, max_row=ws.max_row), start=ws.max_row - len(abreviaciones) + 1):
        for col_num, cell in enumerate(row, start=1):
            cell.style = bold_money_style
            if cell.value is not None:
                # Obtener el color correspondiente para la abreviación corta actual
                color = abreviaciones_colores_cortas.get(cell.value, "FFFFFF")  # Por defecto, color blanco
                cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
    
    sheet = wb['Sheet']
    wb.remove(sheet)
    wb.save(response)

    return(response)