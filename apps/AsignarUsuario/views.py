from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import VallEmpleado 
from django.db.models import Q
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from datetime import datetime
import time


@login_required
def solicitud(request):
    # Aquí la lógica para mostrar la página de inicio
    
    
        
    empleados = []
    empleados = VallEmpleado.objects.exclude(username__isnull=True).exclude(username='')
    
   # print(empleados)
    context = {
        'empleados' : empleados,
        'usersAdmin': empleados.filter( nombre_direccion='Administración'),
        'usersIng': empleados.filter( nombre_direccion='Ingeniería'),
        'usersDCASS': empleados.filter( nombre_direccion='Calidad, Ambiental, Seguridad y Salud'),
        'usersPS': empleados.filter( nombre_direccion='Proyectos Especiales'),
        'active_page': 'solicitud',
        'nombre_usuario': nameUser(request),
        'foto':photoUser(request),
        'Categoria': Categoria(request)
    }
    return render(request, 'personal.html',context)

@login_required
def solicitudNuevos(request):
    # Aquí la lógica para mostrar la página de inicio
    empleados = []
    empleados = VallEmpleado.objects.filter(Q(username__isnull=True) )

   # print(empleados)
    context = {
        'empleados' : empleados,
        'usersAdmin': empleados.filter( nombre_direccion='Administración'),
        'usersIng': empleados.filter( nombre_direccion='Ingeniería'),
        'usersDCASS': empleados.filter( nombre_direccion='Calidad, Ambiental, Seguridad y Salud'),
        'usersPS': empleados.filter( nombre_direccion='Proyectos Especiales'),
        'active_page': 'Nsolicitud',
        'nombre_usuario': nameUser(request),
        'foto':photoUser(request),
        'Categoria': Categoria(request)
    }
    return render(request, 'nuevoPersonal.html',context)


def nameUser(request):
    if request.user.is_authenticated:
        nombreUsuario = request.user.first_name+" "+request.user.last_name 
    
    return  nombreUsuario



@login_required
def enviar_correo(request):
    if request.method == 'POST':
        current_year = datetime.now().year
        dato1 = request.POST.get('nombre')
        dato2 = request.POST.get('puesto')
        observaciones = request.POST.get('observaciones')

        # Checkbox: Almacena los valores seleccionados en una lista
        sistemas_seleccionados = [
            sistema for sistema in ['CONDOR', 'CostoV2', 'EIMyPs', 'Proveedores (Módulo LPG)', 'Reporting Service', 'Sap B1 Web', 'SAPAI', 'SCORE', 'opcion9', 'SIROC', 'SISS', 'Equipo de Cómputo']
            if request.POST.get(sistema) == 'on'
        ] 
        print(sistemas_seleccionados)
        # Preparar el contexto para la plantilla
        context = {
            'nombre': dato1, 
            'puesto': dato2,
            'observaciones':observaciones,
            'year': current_year,
            'sistemas':sistemas_seleccionados,
            }

        # Renderizar el contenido HTML
        html_content = render_to_string('CorreoSolicitudAlta.html', context)
        text_content = strip_tags(html_content)  # Esto crea una versión en texto plano del HTML

        # Crear el correo y añadir tanto el contenido en texto plano como el HTML
        email = EmailMultiAlternatives(
            'Asunto del Mensaje prueba',  # Asunto
            text_content,  # Contenido en texto plano
            'sistemas.iai@grupo-iai.com.mx',  # Email del remitente
            ['manuel.zarate@grupo-iai.com.mx']  # Lista de destinatarios
        )
        email.attach_alternative(html_content, "text/html")
        try:
            time.sleep(30) #para evitar que envie un moton de solicitudes 
            email.send()
            print("Correo enviado correctamente.")
        except Exception as e:
            print(f"Error al enviar correo: {e}")

    return render(request, 'CorreoSolicitudAlta.html', context)


def photoUser(request):
    # Ruta de foto predeterminada
    photo = '/static/img/logo1.png'

    # Comprobar si el usuario está autenticado
    if request.user.is_authenticated:
        # Obtener el nombre de usuario del usuario autenticado
        nombreUsuario = request.user.username

        # Filtrar el objeto VallEmpleado usando el nombre de usuario
        usuarioBD = VallEmpleado.objects.filter(username=nombreUsuario).first()

        # Si se encuentra un usuario en la BD y tiene una ruta de foto, actualizar la ruta de la foto
        if usuarioBD and usuarioBD.RutaFoto_ps:
        
            photo = f'http://intranet.grupo-iai.com.mx:85/SERCAPNUBE/Imagenes/FOTOS/{usuarioBD.RutaFoto_ps}'

    # Devolver la ruta de la foto
    return photo

def Categoria(request):
    usuario=None
    if request.user.is_authenticated:
        # Obtener el nombre de usuario del usuario autenticado
       nombreUsuario = request.user.username

        # Filtrar el objeto VallEmpleado usando el nombre de usuario
       usuarioBD = VallEmpleado.objects.filter(username=nombreUsuario).first()

        # Si se encuentra un usuario en la BD
       if usuarioBD:
            usuario = usuarioBD.Nombre_ct


    return usuario

    