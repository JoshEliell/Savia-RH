from django.shortcuts import render

from django.shortcuts import render,redirect
#verificar autenticacion del usuario
from django.contrib.auth.decorators import login_required
#se importa los modelos de la otra app
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.serializers import serialize
import json
from datetime import datetime
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Sum
import os
import logging
from proyecto.models import Distrito,Perfil,Puesto,UserDatos,Catorcenas,DatosBancarios
from .models import Categoria,Subcategoria,Bono,Solicitud,BonoSolicitado,Requerimiento
from revisar.models import AutorizarSolicitudes
from .forms import SolicitudForm,BonoSolicitadoForm,RequerimientoForm,AutorizarSolicitudesUpdateForm,AutorizarSolicitudesGerenteUpdateForm,BonoSolicitadoPuestoForm
from django.db import connection
from django.core.paginator import Paginator
from .filters import SolicitudFilter,AutorizarSolicitudesFilter,BonoSolicitadoFilter
from django.db.models import Max
from django.db.models import Subquery, OuterRef
from django.http import Http404
import datetime
from datetime import date, timedelta
from django.db.models import Q
#Excel
from openpyxl import Workbook
import openpyxl
from openpyxl.chart import PieChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.chart.label import DataLabelList
from openpyxl.drawing.image import Image
from openpyxl.styles import NamedStyle, Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from django.db.models.functions import Concat
from django.db.models import Value
from django.db.models import Sum
from django.db.models import Count
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.http import HttpResponseRedirect
from datetime import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import date
#pillow - comprimir imagenes
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
#envio de correos
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
# PyMuPDF - comprimir pdfs
import fitz  # PyMuPDF
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import io


#Pagina inicial de los esquemas de los bonos
@login_required(login_url='user-login')
def inicio(request):
    
    bonos = Categoria.objects.all();
    
    context= {
        'bonos':bonos,
    }
    
    return render(request,'esquema/inicio.html',context)

#Listar las solicitudes
@login_required(login_url='user-login')
def listarBonosVarilleros(request):    
    #se obtiene el usuario logueado
    usuario = get_object_or_404(UserDatos,user_id = request.user.id)
    ids = [9,10,11]
    
    if usuario.tipo not in [1,2,3]:
        #se obtiene el perfil del usuario logueado
        solicitante = get_object_or_404(Perfil,numero_de_trabajador = usuario.numero_de_trabajador, distrito = usuario.distrito)
        
        subconsulta_ultima_fecha = AutorizarSolicitudes.objects.values('solicitud_id').annotate(
                ultima_fecha=Max('created_at')
            ).filter(solicitud_id=OuterRef('solicitud_id')).values('ultima_fecha')[:1]
        
        if usuario.tipo.id in [9,10,11]:
            #obtiene todas las ultimas autorizaciones de todos los distritos y roles independientemente en el flujo que se encuentre
            autorizaciones = AutorizarSolicitudes.objects.filter(
                created_at=Subquery(subconsulta_ultima_fecha)
            ).select_related('solicitud', 'perfil').filter(
                solicitud__complete = 1
            ).order_by("-created_at")
        elif usuario.tipo.id in [4,5,12]: #rh, supervisor, superintendente adm.
            #obtiene todas las ultimas autorizaciones de su distrito y roles
            autorizaciones = AutorizarSolicitudes.objects.filter(
                created_at=Subquery(subconsulta_ultima_fecha)
            ).select_related('solicitud', 'perfil').filter(
                solicitud__solicitante_id__distrito_id=solicitante.distrito_id, solicitud__complete = 1
                #solicitud__solicitante_id__distrito_id=solicitante.distrito_id,tipo_perfil_id = usuario.tipo.id ,solicitud__complete = 1
            ).order_by("-created_at")
        else:
            #obtiene la ultima autorizacion independientemente en el flujo que se encuentre            
            autorizaciones = AutorizarSolicitudes.objects.filter(
                created_at=Subquery(subconsulta_ultima_fecha)
            ).select_related('solicitud', 'perfil').filter(
                solicitud__solicitante_id__distrito_id=solicitante.distrito_id ,solicitud__complete = 1
                #solicitud__solicitante_id__distrito_id=solicitante.distrito_id,tipo_perfil_id = usuario.tipo.id ,solicitud__complete = 1
            ).order_by("-created_at")
        
        autorizaciones_filter = AutorizarSolicitudesFilter(request.GET, queryset=autorizaciones)
        autorizaciones = autorizaciones_filter.qs
            
        p = Paginator(autorizaciones, 50)
        page = request.GET.get('page')
        salidas_list = p.get_page(page)
        autorizaciones= p.get_page(page)
        
        contexto = {
            'usuario':usuario,
            'autorizaciones':autorizaciones,
            'autorizaciones_filter': autorizaciones_filter,
            'salidas_list':salidas_list,
            'ids': ids
        }
        
        return render(request,'esquema/bonos_varilleros/listar.html',contexto)
    
    else:
        return render(request, 'revisar/403.html')
    
def comprimir_imagen(imagen):
    """
    Comprime una imagen y devuelve un objeto InMemoryUploadedFile.
    
    Args:
    imagen (InMemoryUploadedFile): Objeto de imagen subida.
    
    Returns:
    InMemoryUploadedFile: Objeto de imagen comprimida.
    """
    # Abre la imagen usando Pillow
    img = Image.open(imagen)
    
    if img.format != 'JPEG':
        img = img.convert('RGB')
    
    # Crea un flujo de bytes para almacenar la imagen comprimida
    img_temp_output = BytesIO()
    
    ancho_original, alto_original = img.size

    # Hace que el height y width se reduzca a la mitad
    nuevo_ancho = ancho_original // 2
    nuevo_alto = alto_original // 2

    # Redimensionar la imagen
    img = img.resize((nuevo_ancho, nuevo_alto))
    
    # Comprime la imagen y la guarda en el flujo de bytes
    img.save(img_temp_output, format='JPEG', quality=50, optimize=True)  # Puedes ajustar la calidad según tus necesidades
    
    # Restablece el puntero del flujo de bytes al principio
    img_temp_output.seek(0)
    
    # Crea un objeto InMemoryUploadedFile para la imagen comprimida
    img_comprimida = InMemoryUploadedFile(img_temp_output, None, imagen.name.split('.')[0] + 'b.jpg', 'image/jpeg', img_temp_output.getbuffer().nbytes, None)
    
    return img_comprimida

def comprimir_pdf(pdf):
    # Open the PDF using PyMuPDF
    pdf_document = fitz.open(stream=pdf.read(), filetype='pdf')
    
    # Create an in-memory buffer for the compressed PDF
    output_buffer = io.BytesIO()
    
    # Define compression settings (for images)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        images = page.get_images(full=True)
        
        # Dictionary to store the new image data
        new_images = {}
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image['image']
            
            # Convert image bytes to a Pillow Image object
            with Image.open(io.BytesIO(image_bytes)) as image:
                # Convert to RGB (in case it's RGBA or another mode)
                image = image.convert("RGB")
                
                #Redimensionar la imagen
                image = image.resize((image.width // 2, image.height // 2), Image.LANCZOS)  # Use Image.LANCZOS for quality reduction
                
                # Create a new in-memory buffer for the compressed image
                img_buffer = io.BytesIO()
                
                # Save the image with reduced quality using Pillow
                image.save(img_buffer, format='JPEG', quality=80, optimize=True)  # Adjust quality as needed
                
                # Store the new image data
                new_images[xref] = img_buffer.getvalue()
        
        # Remove old images and insert new ones
        for xref, new_img_data in new_images.items():
            # Remove the image
            page.delete_image(xref)
            # Insert the new image
            page.insert_image(page.rect, stream=new_img_data)
    
    # Save the compressed PDF to the buffer
    pdf_document.save(output_buffer)
    pdf_document.close()
    
    # Rewind the buffer to the beginning
    output_buffer.seek(0)
    
    # Obtener la fecha y hora actual
    now = datetime.now()
    # Formatear la fecha como una cadena (por ejemplo, "2024-08-09_15-30-45")
    fecha_formateada = now.strftime("%Y-%m-%d_%H-%M-%S")
    # Crear el nombre del archivo usando la fecha
    nombre_archivo = f"file_{fecha_formateada}.pdf"

    # Create an InMemoryUploadedFile object
    compressed_pdf_file = InMemoryUploadedFile(
        output_buffer,
        None,
        nombre_archivo,
        'application/pdf',
        output_buffer.getbuffer().nbytes,
        None
    )
    
    # Return the buffer with the compressed PDF
    return compressed_pdf_file
    
    
#para crear solicitudes de bonos
@login_required(login_url='user-login')
def crearSolicitudBonos(request):
    #usuario = request.user  
    usuario = get_object_or_404(UserDatos,user_id = request.user.id)
    
    #Todos los supervisores y RH pueden crear solicitudes
    if usuario.tipo_id in (5,4): 
        bonoSolicitadoForm = BonoSolicitadoForm()
        bonoSolicitadoPuestoForm = BonoSolicitadoPuestoForm()
        requerimientoForm = RequerimientoForm()
        #se hace una consulta con los empleados del distrito que pertenecen
        empleados = Perfil.objects.filter(distrito_id = usuario.distrito.id).exclude(baja = 1).order_by('nombres')
        solicitante = Perfil.objects.get(numero_de_trabajador = usuario.numero_de_trabajador, distrito_id = usuario.distrito.id)
        #se carga el formulario en automatico definiendo filtros
        bonoSolicitadoForm.fields["trabajador"].queryset = empleados 
        ultimo_registro = Solicitud.objects.filter(complete = True).values_list('folio', flat=True).last()
        
        if ultimo_registro:
            folio = ultimo_registro + 1 
        else:
            folio = 1
            
        solicitud, created = Solicitud.objects.get_or_create(complete = False, defaults={'complete': False, 'folio':folio,'solicitante_id':solicitante.id, 'total':0.00})
        #Obtiene los bonos que han sido creados en la solicitud
        bonos_solicitados = BonoSolicitado.objects.filter(solicitud_id = solicitud.id)
        lista_archivos = Requerimiento.objects.filter(solicitud_id = solicitud.id)
        
        bonos = Subcategoria.objects.all()
        
        bonos_para_select2 = [
            {
                'id': bono.id,
                'text': str(bono.nombre),
                'soporte': str(bono.soporte)
            } for bono in bonos
        ]
        
        errors = {}
        #Para guardar la solicitud
        
        if request.method == "POST":
            #obtiene un queryset de los archivos de la solicitud
        
            if 'btn_archivos' in request.POST:      
                #Se envian los formularios con datos                   
                form = RequerimientoForm(request.POST, request.FILES)  
                archivos = request.FILES.getlist('url')
                    
                if form.is_valid():
                    #Se recorren los archivos para ser almacenados
                    for archivo in archivos:
                        #obtener el tam del archivo cargado en megas
                        archivo_tam = archivo.size/(1024 * 1024)
                        if archivo.content_type != 'application/pdf' and archivo.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' and archivo.content_type != 'application/vnd.ms-excel':
                            if archivo_tam > 5: # 5 megas
                                documento = comprimir_imagen(archivo)
                            else:
                                documento = archivo
                        #Comprime pdf
                        elif archivo.content_type == 'application/pdf':
                            if archivo_tam > 8: # 8 megas
                                documento = comprimir_pdf(archivo)
                            else:
                                documento = archivo
                        else:
                            documento = archivo
                        #Guarda el archivo
                        requerimiento = Requerimiento.objects.create(
                            solicitud_id = solicitud.id,
                            url = documento,
                        )
                        
                        requerimiento.save()
                        
                    solicitud.complete_requerimiento = True
                    solicitud.save()
                    messages.success(request, "El soporte se adjunto correctamente")
                    return redirect("crearSolicitudBonos") 
                else:
                    # Mensaje de error si el formulario no es válido
                    messages.error(request, 'Favor de verificar el formato del soporte y el tamaño maximo son 10 MB')
                
            elif 'btn_agregar' in request.POST:
                form_solicitud = SolicitudForm(request.POST, instance = solicitud)
                if form_solicitud.is_valid():
                    esquema_bono = request.POST.get('esquemaBono')
                    bono_solicitado, created = BonoSolicitado.objects.get_or_create(solicitud_id=solicitud.id,bono_id = esquema_bono,cantidad = 0)
                    form_bonosolicitado = BonoSolicitadoForm(request.POST,instance=bono_solicitado)
                    if form_bonosolicitado.is_valid():
                        puesto = int(request.POST.get('puesto'))
                        if puesto == 7: # Puesto ID - Todos los que participen en la actividad
                            bono_solicitado.save()
                            # id puesto - todos los que participen en la actividad - dividir la cantidad del bono entre el total de los participantes
                            participantes = BonoSolicitado.objects.filter(solicitud_id = solicitud.id).count()
                            #División
                            reparto = Decimal(bono_solicitado.cantidad/participantes)
                            solicitud.total = bono_solicitado.cantidad
                            solicitud.save()
                            BonoSolicitado.objects.filter(solicitud_id = solicitud.id).update(cantidad=reparto)
                        else:
                            bono_solicitado.bono.id = esquema_bono
                            bono_solicitado.save()
                            total = BonoSolicitado.objects.filter(solicitud_id = solicitud.id).aggregate(total=Sum('cantidad'))['total'] 
                            solicitud.total = total
                            solicitud.save()
                            
            elif 'enviar_solicitud' in request.POST:
                #validacion para subir los soportes
                if solicitud.complete_requerimiento == 0:
                    messages.error(request, 'Falta adjuntar soportes')
                    return redirect(request.META.get('HTTP_REFERER'))
                
                #Se envia la solicitud al superintendente
                superintendente = UserDatos.objects.filter(distrito_id=usuario.distrito.id, tipo_id=6).values_list('numero_de_trabajador',flat=True).first()
                perfil_superintendente = Perfil.objects.filter(numero_de_trabajador = superintendente).values_list('id',flat=True).first()
                
                #se crea la autorizacion
                AutorizarSolicitudes.objects.create(
                    solicitud_id = solicitud.id,
                    perfil_id =  perfil_superintendente,
                    tipo_perfil_id = 6, # superintendente
                    estado_id = 3, # pendiente
                )
                
                #Se guarda la solicitud en complete
                solicitud.complete = 1
                solicitud.save()
                
                messages.success(request, "La solicitud se envio al superintendente")
                return redirect('listarBonosVarilleros')
                
        solicitudForm =  SolicitudForm(instance = solicitud)
    
        contexto = {
            'folio': folio,
            'bonos': bonos_para_select2,
            'usuario':usuario,
            'solicitante':solicitante,
            'solicitudForm':solicitudForm,
            'bonoSolicitadoForm':bonoSolicitadoForm,
            'requerimientoForm':requerimientoForm,
            'bonoSolicitadoPuestoForm':bonoSolicitadoPuestoForm,
            'lista_archivos': lista_archivos,
            'bonos_solicitados': bonos_solicitados,
            'errors':errors,
            'solicitud':solicitud,
        
        } 

        return render(request,'esquema/bonos_varilleros/crear_solicitud.html',contexto)
    
    else:
        return render(request, 'revisar/403.html')
        
    

@login_required(login_url='user-login')  
def verificarSolicitudBonosVarilleros(request,solicitud):
    #usuario = request.user
    usuario = get_object_or_404(UserDatos,user_id = request.user.id)
    #solamente RH y supervisores
    if usuario.tipo.id in (4,5):
        
        perfil = Perfil.objects.filter(numero_de_trabajador=usuario.numero_de_trabajador,distrito_id = usuario.distrito.id).values_list('id',flat=True)
        permiso = Solicitud.objects.filter(solicitante_id=perfil[0], pk=solicitud).values_list('id',flat=True)
        
        #checa el perfil correspondiente para cambiar la solicitud - policy
        if not permiso:
            return render(request, 'revisar/403.html')
        
        #obtener las instancias para poblar los formularios
        solicitud = Solicitud.objects.get(pk=solicitud)
        solicitudForm =  SolicitudForm(instance = solicitud)
        
        #se llaman los formularios para su posterior llenado
        bonoSolicitadoForm = BonoSolicitadoForm()
        bonoSolicitadoPuestoForm = BonoSolicitadoPuestoForm()
        requerimientoForm = RequerimientoForm()
        
        #se hace una consulta con los empleados del distrito que pertenecen
        empleados = Perfil.objects.filter(distrito_id = usuario.distrito.id).exclude(baja = 1).order_by('nombres')
        solicitante = Perfil.objects.get(numero_de_trabajador = usuario.numero_de_trabajador, distrito_id = usuario.distrito.id)
        #se carga el formulario en automatico definiendo filtros
        bonoSolicitadoForm.fields["trabajador"].queryset = empleados 
        
        #se llama la autorizacion relacionada
        autorizacion = AutorizarSolicitudes.objects.select_related('solicitud').filter(solicitud=solicitud).last()
        bonos_solicitados = BonoSolicitado.objects.filter(solicitud_id = solicitud.id)
        lista_archivos = Requerimiento.objects.filter(solicitud_id = solicitud.id)
        
        #Se obtiene los nombres de los bonos
        bonos = Subcategoria.objects.all()
        
        bonos_para_select2 = [
            {
                'id': bono.id,
                'text': str(bono.nombre),
                'soporte': str(bono.soporte)
            } for bono in bonos
        ]
        
        errors = {}
        #Para guardar la solicitud
        if request.method == "POST":
            #obtiene un queryset de los archivos de la solicitud

            if 'btn_archivos' in request.POST:      
                #Se envian los formularios con datos                   
                form = RequerimientoForm(request.POST, request.FILES)  
                archivos = request.FILES.getlist('url')
                
                if form.is_valid():
                    #Se recorren los archivos para ser almacenados
                    for archivo in archivos:
                        #obtener el tam del archivo cargado en megas
                        archivo_tam = archivo.size/(1024 * 1024)
                        if archivo.content_type != 'application/pdf' and archivo.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' and archivo.content_type != 'application/vnd.ms-excel':
                            if archivo_tam > 5: # 5 megas
                                documento = comprimir_imagen(archivo)
                            else:
                                documento = archivo
                        #Comprime pdf
                        elif archivo.content_type == 'application/pdf':
                            if archivo_tam > 8: # 8 megas
                                documento = comprimir_pdf(archivo)
                            else:
                                documento = archivo
                        else:
                            documento = archivo
                        #Guarda el archivo
                        requerimiento = Requerimiento.objects.create(
                            solicitud_id = solicitud.id,
                            url = documento,
                        )
                        
                        requerimiento.save()
                        
                    solicitud.complete_requerimiento = True
                    solicitud.save()
                    messages.success(request, "El soporte se adjunto correctamente")
                    return redirect('verificarSolicitudBonosVarilleros', solicitud=solicitud.id) 
                else:
                    # Mensaje de error si el formulario no es válido
                    messages.error(request, 'Favor de verificar el formato del soporte y el tamaño maximo son 10 MB')
                                
            elif 'btn_agregar' in request.POST:
                form_solicitud = SolicitudForm(request.POST, instance = solicitud)
                if form_solicitud.is_valid():
                    esquema_bono = request.POST.get('esquemaBono')
                    bono_solicitado, created = BonoSolicitado.objects.get_or_create(solicitud_id=solicitud.id,bono_id = esquema_bono,cantidad = 0)
                    form_bonosolicitado = BonoSolicitadoForm(request.POST,instance=bono_solicitado)
                    if form_bonosolicitado.is_valid():
                        puesto = int(request.POST.get('puesto'))
                        if puesto == 7: #
                            bono_solicitado.save()
                            # id puesto - todos los que participen en la actividad - dividir la cantidad del bono entre el total de los participantes
                            participantes = BonoSolicitado.objects.filter(solicitud_id = solicitud.id).count()
                            #División
                            reparto = Decimal(bono_solicitado.cantidad/participantes)
                            solicitud.total = bono_solicitado.cantidad
                            solicitud.save()
                            BonoSolicitado.objects.filter(solicitud_id = solicitud.id).update(cantidad=reparto)
                        else:
                            bono_solicitado.bono.id = esquema_bono
                            bono_solicitado.save()
                            total = BonoSolicitado.objects.filter(solicitud_id = solicitud.id).aggregate(total=Sum('cantidad'))['total'] 
                            solicitud.total = total
                            solicitud.save()
                            
            elif 'actualizar_solicitud' in request.POST:
                print("Enviar la solicitud")
                print(autorizacion.estado)
                autorizacion.estado_id = 3# Estado pendiente
                autorizacion.save()
                messages.success(request, "La solicitud se envio con nuevos cambios al superintendente")
                return redirect('listarBonosVarilleros')
                
        solicitudForm = SolicitudForm(instance = solicitud)
    
        contexto = {
           
            'bonos': bonos_para_select2,
            'usuario':usuario,
            'solicitante':solicitante,
            'solicitudForm':solicitudForm,
            'bonoSolicitadoForm':bonoSolicitadoForm,
            'requerimientoForm':requerimientoForm,
            'bonoSolicitadoPuestoForm':bonoSolicitadoPuestoForm,
            'lista_archivos': lista_archivos,
            'bonos_solicitados': bonos_solicitados,
            'errors':errors,
            'solicitud':solicitud,
            'autorizacion':autorizacion,
        
        } 
            
        
        
        
        
        
        
      

        return render(request, 'esquema/bonos_varilleros/verificar_solicitud.html', contexto)
    
    else:
        return render(request, 'revisar/403.html')
        
#para ver detalles de la solicitud
@login_required(login_url='user-login')
def verDetallesSolicitud(request,solicitud_id):    
    usuario = get_object_or_404(UserDatos,user_id = request.user.id)
    if usuario.tipo not in [1,2,3]:
        #obtener_bono = Solicitud.objects.filter(pk=solicitud_id).values('bono_id').first()
        obtener_bono = Solicitud.objects.filter(pk=solicitud_id).first()
        
        if obtener_bono is None:
            raise Http404("No encontrado") 
        
        #Permisos - Los usuarios pueden ver de todos los distritos - Los demas solo pueden ver de su distrito
        if usuario.tipo.id not in [9,10,11] and usuario.distrito.id != obtener_bono.solicitante.distrito.id:
            return render(request, 'revisar/403.html')
        
        soporte_detalles = Subcategoria.objects.filter(pk=obtener_bono.bono_id).values('soporte').first()
        soporte = soporte_detalles['soporte']
        
        #los bonos solicitados
        bonos = BonoSolicitado.objects.filter(solicitud_id = solicitud_id)
        #los archivos
        requerimientos = Requerimiento.objects.filter(solicitud_id = solicitud_id)
        
        #busca la ultima solicitud con relacion a sus modelos     
        autorizaciones = AutorizarSolicitudes.objects.filter(
            solicitud_id=solicitud_id
        ).annotate(
            ultima_fecha=Max('created_at')
        ).order_by('-ultima_fecha').first()
                
        #Para obtener el rol del solicitante
        no_trabajador = autorizaciones.solicitud.solicitante.numero_de_trabajador
        distrito = autorizaciones.solicitud.solicitante.distrito.id
        perfiles = UserDatos.objects.filter(distrito_id = distrito, numero_de_trabajador = no_trabajador);
        for p in perfiles:
            print("este es el perfil que choca: ",p)
            print(p.distrito)
            print(p.numero_de_trabajador)
            print("===========")
        rol = UserDatos.objects.get(distrito_id = distrito, numero_de_trabajador = no_trabajador)
    
        rol = rol.tipo
        print(rol)
        
        #se carga el formulario con datos iniciales
        autorizarSolicitudesUpdateForm = AutorizarSolicitudesUpdateForm(initial={'estado':autorizaciones.estado.id,'comentario':autorizaciones.comentario})
        autorizarSolicitudesGerenteUpdateForm = AutorizarSolicitudesGerenteUpdateForm(initial={'estado':autorizaciones.estado.id,'comentario':autorizaciones.comentario})
            
        contexto = {
            "usuario":usuario,
            "autorizaciones":autorizaciones,
            "bonos":bonos,
            "requerimientos": requerimientos,
            "autorizarSolicitudesUpdateForm":autorizarSolicitudesUpdateForm,
            "autorizarSolicitudesGerenteUpdateForm":autorizarSolicitudesGerenteUpdateForm,
            "soporte":soporte,
            "rol":rol
        }
        
        return render(request,'esquema/bonos_varilleros/detalles_solicitud.html',contexto)
    else:
        return render(request, 'revisar/403.html')

#lista bonos aprobados
@login_required(login_url='user-login')
def listarBonosVarillerosAprobados(request):
    #se obtiene el usuario logueado
    usuario = get_object_or_404(UserDatos,user_id = request.user.id)
    #ids de los perfiles - ver toda la info del sistema
    ids = [9,10,11]
    
    #Queries de bonos aprobados dependiento el rol
    if usuario.tipo.id in (9,10,11):
        #obtiene todos los bonos aprobados de todos los distritos        
        bonos_solicitados = BonoSolicitado.objects.filter(
            solicitud__autorizarsolicitudes__isnull=False,
            solicitud__autorizarsolicitudes__estado_id=1,
            solicitud__autorizarsolicitudes__tipo_perfil_id=8,
            #solicitud__autorizarsolicitudes__updated_at__range=(fecha_inicial, fecha_final)
        ).order_by('-trabajador')
          
    elif usuario.tipo.id in (4,12,8):
        #obtiene todos los bonos aprobados de un solo distrito al que pertenece 
        bonos_solicitados = BonoSolicitado.objects.filter(
            solicitud__autorizarsolicitudes__isnull=False,
            solicitud__autorizarsolicitudes__estado_id=1,
            solicitud__autorizarsolicitudes__tipo_perfil_id=8,
            solicitud__autorizarsolicitudes__perfil__distrito_id=usuario.distrito.id,
            #solicitud__autorizarsolicitudes__updated_at__range=(fecha_inicial,fecha_final)
        ).order_by('-trabajador')
    else:
        return render(request, 'revisar/403.html')
    
    #Preparar los bonos aprobados para ser mostrados
    bonosolicitado_filter = BonoSolicitadoFilter(request.GET, queryset=bonos_solicitados)
    bonos_solicitados = bonosolicitado_filter.qs
    
    total_monto = bonos_solicitados.aggregate(total_monto=Sum('cantidad'))['total_monto']
    cantidad_bonos_aprobados = bonos_solicitados.count()
    
    fecha_inicial = request.GET.get('fecha_inicial_catorcena', None)
    fecha_final = request.GET.get('fecha_final_catorcena', None)
        
    if request.method =='POST' and 'excel' in request.POST:
        return convert_excel_bonos_aprobados(bonos_solicitados,fecha_inicial,fecha_final,total_monto,cantidad_bonos_aprobados)
    
    p = Paginator(bonos_solicitados, 50)
    page = request.GET.get('page')
    salidas_list = p.get_page(page)
    bonos_solicitados = p.get_page(page)
    
    contexto = {
        'salidas_list':salidas_list,
        'bonosolicitado_filter':bonosolicitado_filter,
        'cantidad_bonos_aprobados':cantidad_bonos_aprobados,
        'total_monto':total_monto,
        #'catorcena':catorcena_actual,
        'usuario':usuario,
        'ids':ids,
        'bonos_solicitados':bonos_solicitados,
        'fecha_inicial':fecha_inicial,
        'fecha_final':fecha_final
    }
    
    return render(request,'esquema/bonos_varilleros/listar_bonos_aprobados.html',contexto)

#generar reportes bonos aprobados
@login_required(login_url='user-login')
def generarReporteBonosVarillerosAprobados(request):
    
    #se obtiene el usuario logueado
    usuario = get_object_or_404(UserDatos,user_id = request.user.id)
    ids = [9,10,11]
    
    print(usuario.tipo.id)
    
    #Flujo de las autorizaciones y permisos
    if usuario.tipo.id in (9,10,11,12): #
        #se buscan los perfiles acredores al bono
        folios = Solicitud.objects.filter(fecha_autorizacion__isnull=False).values('folio')
    elif usuario.tipo.id in (4,12,8): #RH, SA, GE
        folios = Solicitud.objects.filter(fecha_autorizacion__isnull=False, solicitante__distrito_id = usuario.distrito.id).values('folio')
    else:
        return render(request, 'revisar/403.html')
        
    #if not folios:
    #    return render(request, 'revisar/403.html')
    
    #se prepara un 
    solicitudes = []
    for item in folios:
        solicitud_id = item['folio']
        solicitudes.append(solicitud_id)
        
    bonos = BonoSolicitado.objects.filter(solicitud_id__in = solicitudes).order_by('trabajador_id')
            
    bonosolicitado_filter = BonoSolicitadoFilter(request.GET, queryset=bonos) 
    bonos = bonosolicitado_filter.qs
    
    for b in bonos:
        print(b)
            
    bono = bonos.last()
    
    if bono is not None:
        catorcena = Catorcenas.objects.filter(fecha_inicial__lte=bono.solicitud.fecha_autorizacion, fecha_final__gte=bono.solicitud.fecha_autorizacion).first()
    else:
        catorcena = None
        
    total_monto = bonos.aggregate(total_monto=Sum('cantidad'))['total_monto']
    cantidad_bonos_aprobados = bonos.count()
        
    if request.method =='POST' and 'excel' in request.POST:
        return convert_excel_bonos_aprobados(bonos,catorcena,total_monto,cantidad_bonos_aprobados)
    
    p = Paginator(bonos, 50)
    page = request.GET.get('page')
    salidas_list = p.get_page(page)
    bonos = p.get_page(page)
        
    contexto = {
        'bonos':bonos,
        'bonosolicitado_filter':bonosolicitado_filter,
        'cantidad_bonos_aprobados':cantidad_bonos_aprobados,
        'catorcena':catorcena,
        'total_monto':total_monto,
        'salidas_list':salidas_list,
        'usuario':usuario,
        'ids':ids
    }
            
    return render(request,'esquema/bonos_varilleros/generar_reporte_bonos.html',contexto)

#para remover bonos agregados
@login_required(login_url='user-login')
def removerBono(request,bono_id):
    #hacer el complete requerimiento a 0 - contar el numero de archivos cuando es 0
    if request.method == "POST":
        
        usuario = get_object_or_404(UserDatos,user_id = request.user.id)
        
        if usuario.tipo.id in (4,5):
            try:
                bono_solicitado = BonoSolicitado.objects.get(pk=bono_id)
                bandera = False #Se utiliza para saber si se realiza una division o suma acumulativa
                
                if bono_solicitado.bono.puesto.id == 7: # id puesto - todos los que participen en la actividad
                    #indica que se hara una division
                    bandera = True
                    solicitud_id = bono_solicitado.solicitud.id
                    bono_solicitado.delete()
                    #obtengo el total de la solicitud y ese total es divido entre en numero de empleados
                    total = Solicitud.objects.filter(pk = solicitud_id).values_list('total',flat=True) #recuerda acceder al valor como total[0]
                    participantes = BonoSolicitado.objects.filter(solicitud_id = solicitud_id).count()
                    if participantes > 0: #No se puede dividir entre 0
                        reparto = Decimal(total[0]/participantes)
                        BonoSolicitado.objects.filter(solicitud_id = solicitud_id).update(cantidad=reparto)
                        return JsonResponse({'bono_id': bono_id,'total':total[0], 'bandera':bandera,'reparto':reparto} ,status=200, safe=True)  
                    else:
                        return JsonResponse({'bono_id': bono_id,'total':0,'bandera':bandera,'reparto':0} ,status=200, safe=True)
                    
                else:
                    #obtengo el id de la solicitud
                    solicitud_id = bono_solicitado.solicitud_id
                    #se elimina el registro del bonosolicitud
                    bono_solicitado.delete()
                    #se realiza la suma con los que queda en la BD
                    total = BonoSolicitado.objects.filter(solicitud_id = solicitud_id).aggregate(total=Sum('cantidad'))['total'] or 0
                    #se actualza la solicitud el total
                    Solicitud.objects.filter(pk = solicitud_id).update(total = total)  
                    return JsonResponse({'bono_id': bono_id,'total':total, 'bandera':bandera} ,status=200, safe=True)              
                
            except:
                return JsonResponse({'mensaje': 'No encontrado'}, status=404,safe=True)
        else:
            return JsonResponse({'mensaje': 'Prohibido'}, status=403,safe=True)

#para remover bonos verificar     
@login_required(login_url='user-login')
def removerBonoVerificar(request,bono_id):
    #hacer el complete requerimiento a 0 - contar el numero de archivos cuando es 0
    if request.method == "POST":
        
        usuario = get_object_or_404(UserDatos,user_id = request.user.id)
        
        if usuario.tipo.id in (4,5):
            try:
                print("Este es el bono: ", bono_id)
                bono = BonoSolicitado.objects.get(pk=bono_id)
                solicitud = Solicitud.objects.get(pk=bono.solicitud_id)
                if bono.puesto.id == 19: #ID puesto - todos los que participen en la actividad
                    print("Bono reparto")
                    bandera = 0 #se utiliza para ocultar la tabla del bono
                    participantes = BonoSolicitado.objects.filter(solicitud_id = bono.solicitud.id).count()#se cuenta el numero
                    bandera = participantes
                    participantes-=1 #se resta porque al final se le quita uno y se debe quedar la cuenta
                    solicitud = Solicitud.objects.get(pk=bono.solicitud.id)
                    if participantes == 0:
                        participantes = 1
                    reparto = Decimal(solicitud.total/participantes) #se hace la división
                    BonoSolicitado.objects.filter(solicitud_id = bono.solicitud.id).update(cantidad=reparto)
                    bono.delete()
                    return JsonResponse({'bono_id': bono_id,'total':solicitud.total, 'reparto':True, 'monto':reparto, 'participantes':participantes, 'bandera':bandera} ,status=200, safe=True)
                
                else:    
                    print("Cualquier bono")
                    solicitud.total -= bono.cantidad
                    solicitud.save()
                    bono.delete()
                
                    return JsonResponse({
                        'bono_id': bono_id,
                        'total':solicitud.total, 
                        'reparto':False} ,status=200, safe=True)
            
            except:
                return JsonResponse({'mensaje': 'No encontrado'}, status=404,safe=True)
        else:
            return JsonResponse({'mensaje': 'Prohibido'}, status=403,safe=True)
        
        
#para remover archivos agregados
@login_required(login_url='user-login')
def removerArchivo(request,archivo_id):
    if request.method == "POST":
        
        usuario = get_object_or_404(UserDatos,user_id = request.user.id)
        if usuario.tipo.id in (4,5):
            try:
                archivo = get_object_or_404(Requerimiento,pk=archivo_id)
                
                if os.path.isfile(archivo.url.path):
                    os.remove(archivo.url.path)
                    
                archivo.delete()
                            
                return JsonResponse({"archivo_id":archivo_id},status=200,safe=False)
            except:
                return JsonResponse({'mensaje':'objecto no encontrado'},status=404,safe=True)
            
        else:
            return JsonResponse({'mensaje': 'Prohibido'}, status=403,safe=True)        
        
#GENERACION DE REPORTES EN EXCEL
def convert_excel_bonos_aprobados(bonos,fecha_incial,fecha_final,total_monto,cantidad_bonos_aprobados):
    response= HttpResponse(content_type = "application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename = Reporte_bonos_varilleros_aprobados_' + str(date.today())+'.xlsx'
    wb = Workbook()
    ws = wb.create_sheet(title='Reporte')
    #Comenzar en la fila 1
    row_num = 1
    
    #Create heading style and adding to workbook | Crear el estilo del encabezado y agregarlo al Workbook
    head_style = NamedStyle(name = "head_style")
    head_style.font = Font(name = 'Arial', color = '00FFFFFF', bold = True, size = 11)
    head_style.fill = PatternFill("solid", fgColor = '00003366')
    wb.add_named_style(head_style)
    #Create body style and adding to workbook
    body_style = NamedStyle(name = "body_style")
    body_style.font = Font(name ='Calibri', size = 10)
    wb.add_named_style(body_style)
    #Create messages style and adding to workbook
    messages_style = NamedStyle(name = "mensajes_style")
    messages_style.font = Font(name="Arial Narrow", size = 11)
    wb.add_named_style(messages_style)
    #Create date style and adding to workbook
    number_style = NamedStyle(name='number_style', number_format='#,##0')
    date_style = NamedStyle(name='date_style', number_format='DD/MM/YYYY HH:MM')
    date_style.font = Font(name ='Calibri', size = 10)
    wb.add_named_style(date_style)
    money_style = NamedStyle(name='money_style', number_format='$ #,##0.00')
    money_style.font = Font(name ='Calibri', size = 10)
    wb.add_named_style(money_style)
    money_resumen_style = NamedStyle(name='money_resumen_style', number_format='$ #,##0.00')
    money_resumen_style.font = Font(name ='Calibri', size = 14, bold = True)
    wb.add_named_style(money_resumen_style)
    dato_style = NamedStyle(name='dato_style',number_format='DD/MM/YYYY')
    dato_style.font = Font(name="Arial Narrow", size = 11)
    
    
    
    #se crea el encabezado de la tabla en excel 
    columns = ['Folio','Fecha emisión','Fecha aprobación','# Trabajador','Nombre','No. de cuenta','No. de tarjeta','Banco','Distrito','Bono','Puesto','Cantidad']
    
    #se añade el ancho de cada columna
    for col_num in range(len(columns)):
        (ws.cell(row = row_num, column = col_num+1, value=columns[col_num])).style = head_style
        if col_num < 4:
            ws.column_dimensions[get_column_letter(col_num + 1)].width = 10
        if col_num == 4:
            ws.column_dimensions[get_column_letter(col_num + 1)].width = 30
        else:
            ws.column_dimensions[get_column_letter(col_num + 1)].width = 15
            
    columna_max = len(columns)+2
    
    (ws.cell(column = columna_max, row = 1, value='{Reporte Creado Automáticamente por Savia RH. UH}')).style = messages_style
    (ws.cell(column = columna_max, row = 2, value='{Software desarrollado por Vordcab S.A. de C.V.}')).style = messages_style
    (ws.cell(column = columna_max, row = 3, value='')).style = messages_style
    (ws.cell(column = columna_max, row = 5, value=f'Fecha: {fecha_incial} - {fecha_final}')).style = dato_style
    (ws.cell(column = columna_max, row = 6, value=f'Bonos aprobados: {cantidad_bonos_aprobados}')).style = messages_style
    (ws.cell(column = columna_max, row = 7, value=f'Total $: {total_monto}')).style = messages_style
    ws.column_dimensions[get_column_letter(columna_max)].width = 45
    ws.column_dimensions[get_column_letter(columna_max + 1)].width = 45
    ws.column_dimensions[get_column_letter(columna_max + 1)].width = 45
    ws.column_dimensions[get_column_letter(columna_max + 1)].width = 45
    ws.column_dimensions[get_column_letter(columna_max + 1)].width = 45
    
    rows = []
    
    #aqui se recorre el query de los bonos y se debe formatear los objectos a un tipo de dato
    for bono in bonos:

        row = (
            bono.solicitud.folio,
            bono.fecha.strftime('%Y-%m-%d %H:%M'),
            bono.solicitud.fecha_autorizacion.strftime('%Y-%m-%d %H:%M'),
            str(bono.trabajador.numero_de_trabajador),
            str(bono.trabajador),
            bono.trabajador.status.datosbancarios.no_de_cuenta,
            bono.trabajador.status.datosbancarios.numero_de_tarjeta,
            str(bono.trabajador.status.datosbancarios.banco),
            str(bono.bono.distrito),
            str(bono.solicitud.bono),
            str(bono.bono.puesto),
            bono.cantidad
        )
        rows.append(row)
        
        #aqui se empieza el recorrido para el llenado de datos de acuerdo a su tipo
        for row_num, row in enumerate(rows, start=2):
            for col_num, value in enumerate(row, start=1):
                if col_num == 1:
                    ws.cell(row=row_num, column=col_num, value=value).style = number_style
                elif col_num == 2 or col_num == 3:
                    ws.cell(row=row_num, column=col_num, value=value).style = date_style
                elif col_num <= 9:
                    ws.cell(row=row_num, column=col_num, value=value).style = body_style
                else:
                    ws.cell(row=row_num, column=col_num, value=value).style = money_style
    
    sheet = wb['Sheet']
    wb.remove(sheet)
    wb.save(response)
    
    return(response)

@login_required(login_url='user-login')
def tabuladorBonos(request):
    
    return render(request, 'esquema/crear_bonos/tabulador_bonos.html')

@login_required(login_url='user-login')
def get_puestos(request):    
    try:
        usuario = request.user
        bono_id = request.GET.get('bono_id')
        folio = request.GET.get('folio')
        data = []
        
        if bono_id:
            
            if int(bono_id) in (1,2):#IDS DEL MODELO ESQUEMA_SUBATEGORIA - evic extracion, evic introduccion
                bonos_solicitados = BonoSolicitado.objects.filter(solicitud__folio = folio).select_related('bono__puesto').values_list('bono__puesto_id',flat=True)
                 #Trae todos los bonos por puesto por distrito, estado 1 = baja | 0 = activo - se excluye el puesto para este caso
                puestos_qs = Bono.objects.filter(esquema_subcategoria = bono_id,distrito_id = usuario.userdatos.distrito.id,estado = 0).exclude(puesto_id__in = list(bonos_solicitados)).values('id','puesto__id','puesto__puesto','importe')
            else:
                #Trae todos los bonos por puesto por distrito, estado 1 = baja | 0 = activo
                puestos_qs = Bono.objects.filter(esquema_subcategoria = bono_id,distrito_id = usuario.userdatos.distrito.id,estado = 0).values('id','puesto__id','puesto__puesto','importe')
            
            for puesto in puestos_qs:
                puesto['importe'] = str(puesto['importe'])
            data = list(puestos_qs)
            
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
