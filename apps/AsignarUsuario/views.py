from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import VallEmpleado 
from apps.RegistroModulo.models import TRegistroDeModulo 
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
from django.utils import timezone
from .utils import AtributosDeEmpleado
from django.contrib.auth.models import User
from cryptography.fernet import Fernet

empleado = AtributosDeEmpleado()
ENCRYPTION_KEY_DESCRIPCION = b'VVsQPaM9IhXYrWNwLyKkAnmJdzdFR8R0MwdvZpHGsA8='
ENCRYPTION_KEY_NOMBRE = b'o2GwoZ4O2UyRvsWTK7owoZKHOBQU2TbmYHUkHI1OWMs='

@login_required
def solicitud(request):
    # Aquí la lógica para mostrar la página de inicio
    
    
        
    empleados = []
    empleados = VallEmpleado.objects.exclude(username__isnull=True).exclude(username='')
    encabezados ={
        'title' :'Empleados de Grupo IAI  - IDIAI',
        'Encabezado' :'Personal de Grupo IAI:',
        'SubEncabezado' :'Plataforma para solicitar permisos de usuarios para el personal del Grupo IAI',
        'EncabezadoNav' :'Solicitud',
        'EncabezadoCard' : 'Solicitar Permisos',
        
    }
   # print(empleados)
    context = {
        'empleados' : empleados,
        'usersAdmin': empleados.filter( nombre_direccion='Administración'),
        'usersIng': empleados.filter( nombre_direccion='Ingeniería'),
        'usersDCASS': empleados.filter( nombre_direccion='Calidad, Ambiental, Seguridad y Salud'),
        'usersPS': empleados.filter( nombre_direccion='Proyectos Especiales'),
        'active_page': 'solicitud',
        'nombre_usuario': empleado.nameUser(request),
        'foto':empleado.photoUser(request),
        'Categoria': empleado.Categoria(request),
        'encabezados' :encabezados,
        'ActiveDirectory' :False
    }
    return render(request, 'personal.html',context)

@login_required
def solicitudNuevos(request):
    # Aquí la lógica para mostrar la página de inicio
    empleados = []
    empleados = VallEmpleado.objects.filter(Q(username__isnull=True) )
    encabezados ={
        'title' :'Empleados de Grupo IAI  - IDIAI',
        'Encabezado' :'Nuevo personal de Grupo IAI:',
        'SubEncabezado' :'Plataforma para solicitar los usuarios para el personal del Grupo IAI',
        'EncabezadoNav' :'Solicitud',
        'EncabezadoCard' : 'Solicitar Alta',
        
    }
   # print(empleados)
    context = {
        'empleados' : empleados,
        'usersAdmin': empleados.filter( nombre_direccion='Administración'),
        'usersIng': empleados.filter( nombre_direccion='Ingeniería'),
        'usersDCASS': empleados.filter( nombre_direccion='Calidad, Ambiental, Seguridad y Salud'),
        'usersPS': empleados.filter( nombre_direccion='Proyectos Especiales'),
        'active_page': 'Nsolicitud',
        'nombre_usuario': empleado.nameUser(request),
        'foto':empleado.photoUser(request),
        'Categoria': empleado.Categoria(request),
        'encabezados' :encabezados,
        'ActiveDirectory' :False
    }
    return render(request, 'personal.html',context)

@login_required
def nuevosIDIAI(request):
    # Aquí la lógica para mostrar la página de inicio
    if request.method == 'POST':
        nombre_usuario = request.POST['nombre_usuario'].upper()
        nombre_pila = request.POST['nombre_pila']
        apellido = request.POST['apellido']
        nombre_completo = request.POST['nombre_completo']
        email = request.POST['email']
        password = request.POST['password']
        nombre_inicio_sesion = request.POST['nombre_inicio_sesion']
        departamento = request.POST['departamento']
        puesto = request.POST['puestoCT']
        print( nombre_usuario,nombre_pila,apellido,nombre_completo,email,password,nombre_inicio_sesion,departamento,puesto )
        user, created = User.objects.get_or_create(username= nombre_usuario, defaults={
                'email':email,
                'first_name': nombre_pila,
                'last_name': apellido,
                'is_active': True,
                'is_superuser': False,
                'is_staff': False,
                'last_login': None,
                'date_joined': timezone.now(),
            })
        if created:
            user.set_password(password )  # Asegúrate de que la contraseña esté en texto plano aquí
            user.save()
            n = Fernet(ENCRYPTION_KEY_NOMBRE)
            f = Fernet(ENCRYPTION_KEY_DESCRIPCION)
            nombre_cifrado = n.encrypt(nombre_usuario.encode()).decode()
            descripcion_cifrado = f.encrypt(password.encode()).decode()
            nombreCompleto = nombre_completo
            
            nuevo_usuario, created2 = TRegistroDeModulo.objects.get_or_create(
                nombre_completo=nombreCompleto,
                defaults={
                    '_descripcion': descripcion_cifrado, '_nombre':nombre_cifrado,
                    
                }
            )
            if created2:
                nuevo_usuario.save()
                messages.success(request,f"Usuario creado:{nombre_usuario}") # 
            else:
                messages.error(request,f"Usuario existente en el Modulo: {nombre_usuario}")
              # 
                 
            
            
            
            return redirect('nuevousuario') 
        else:
            messages.error(request,f"Usuario existente: {nombre_usuario}")
            return redirect('nuevousuario') 
        
    
        
    
    empleados = []
    empleados = VallEmpleado.objects.filter(Q(username__isnull=True) )
    encabezados ={
        'title' :'Empleados de Grupo IAI  - IDIAI-',
        'Encabezado' :'Nuevo personal de Grupo IAI:',
        'SubEncabezado' :'Plataforma para Agregar  usuarios a  IDIAI',
        'EncabezadoNav' :'Agregar',
        'EncabezadoCard' : 'Agregar Usuario IDIAI',
        
    }
   # print(empleados)
    context = {
        'empleados' : empleados,
        'usersAdmin': empleados.filter( nombre_direccion='Administración'),
        'usersIng': empleados.filter( nombre_direccion='Ingeniería'),
        'usersDCASS': empleados.filter( nombre_direccion='Calidad, Ambiental, Seguridad y Salud'),
        'usersPS': empleados.filter( nombre_direccion='Proyectos Especiales'),
        'active_page': 'Nsolicitud',
        'nombre_usuario': empleado.nameUser(request),
        'foto':empleado.photoUser(request),
        'Categoria': empleado.Categoria(request),
        'encabezados' :encabezados,
        'ActiveDirectory' :True
    }
    return render(request, 'nuevoPersonal.html',context)


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


    