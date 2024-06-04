from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import VallEmpleado , VAllReclutamiento
from apps.AsignarUsuario.models import  TRegistroAccionesModulo 
from apps.RegistroModulo.models import TRegistroDeModulo 
from apps.ActiveDirectory.views import  SelectDepartamento , notificacionCorreo

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
import os
import base64

empleado = AtributosDeEmpleado()
selectDepartamento= SelectDepartamento()
ENCRYPTION_KEY_DESCRIPCION =os.environ.get('KEY_DESCRIPCION').encode()
ENCRYPTION_KEY_NOMBRE = os.environ.get('KEY_NOMBRE').encode()




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
    empleados = []
    empleados = VallEmpleado.objects.filter(Q(username__isnull=True) )
    encabezados ={
        'title' :'Empleados de Grupo IAI  - IDIAI-',
        'Encabezado' :'Nuevo personal de Grupo IAI:',
        'SubEncabezado' :'Plataforma para Agregar  usuarios a  IDIAI',
        'EncabezadoNav' :'Agregar',
        'EncabezadoCard' : 'Agregar Usuario IDIAI',
        'titulomodal1':'Crear Usuario de IDIAI'
        
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
        'ActiveDirectory' :True,
        'selectDepartamento': selectDepartamento
    }
  
  
  
    # Aquí la lógica para mostrar la página de inicio
    if request.method == 'POST':
        nombre_usuario = request.POST['nombre_usuario'].strip().title()
        nombre_pila = request.POST['nombre_pila'].strip().title()
        apellido = request.POST['apellido'].strip().title()
        nombre_completo = request.POST['nombre_completo'].strip().title()
        email = request.POST['email'].lower().strip()
        password = request.POST['password']
        nombre_inicio_sesion = request.POST['nombre_inicio_sesion'].lower().strip()
        departamento = request.POST['departamento']
        puesto = request.POST['puestoCT']
        #print( nombre_usuario,nombre_pila,apellido,nombre_completo,email,password,nombre_inicio_sesion,departamento,puesto )
        LugarCreado=" "
        LugarNoCreado=" "
        user, created = User.objects.get_or_create(username= nombre_inicio_sesion, defaults={
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
            LugarCreado+=" IDIAI V2 "
            user.set_password(password )  # Asegúrate de que la contraseña esté en texto plano aquí
            user.save()
            n = Fernet(ENCRYPTION_KEY_NOMBRE)
            f = Fernet(ENCRYPTION_KEY_DESCRIPCION)
            nombre_cifrado = n.encrypt(nombre_inicio_sesion.encode().strip()).decode()
            descripcion_cifrado = f.encrypt(password.encode()).decode()
            nombreCompleto = nombre_completo
            messages.success(request,f"Usuario creado en  {LugarCreado} :{nombre_usuario}") # 
            imprimir(f"Usuario creado en {LugarCreado}:{nombre_usuario}")
            mensajeCont =f"El usuario '{nombre_usuario}' de {nombre_completo} fue creado en IDIAI V2"
            insertar_registro_accion(
                            empleado.nameUser(request),
                            'Modulo AD',
                            'Crear',
                            f"El usuario '{nombre_usuario}' fue creado en IDIAI V2",
                            get_client_ip(request),
                            request.META.get('HTTP_USER_AGENT'),
                            'N/A'
                            )  
            nuevo_usuario, created2 = TRegistroDeModulo.objects.get_or_create(
                _nombre=nombre_cifrado,
                defaults={
                    '_descripcion': descripcion_cifrado, 'nombre_completo':nombreCompleto,
                    
                }
            )
            notificacionCorreo(request,f'IDIAI V2 creación del usuario {nombre_usuario}','Creación de usuario',mensajeCont)
            if created2:
                nuevo_usuario.save()
                LugarCreado+=" y Modulo "
                messages.success(request,f"Usuario creado en  {LugarCreado} :{nombre_usuario}") # 
                imprimir(f"Usuario creado en {LugarCreado}:{nombre_usuario}")
                insertar_registro_accion(
                            empleado.nameUser(request),
                            'Modulo AD',
                            'Crear',
                            f"El usuario '{nombre_usuario}' fue creado en el modulo",
                            get_client_ip(request),
                            request.META.get('HTTP_USER_AGENT'),
                            'N/A'
                            ) 
            else:
                messages.error(request,f"Usuario existente en el Modulo: {nombre_usuario}")
              # 
                 
            
            
            
           # return redirect(request, 'nuevoPersonal.html',context) 
        else:
            LugarNoCreado+= ' IDIAI V2 y Modulo '
            messages.error(request,f"Usuario existente en {LugarNoCreado}: {nombre_usuario}")
          #  return redirect(request, 'nuevoPersonal.html',context) 
        
    
        
    
  
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


def imprimir(mensaje): #funcion para imprimir en la consola  en modo desarrollador 
    #if settings.DEBUG:
    print(mensaje)
        
        
def insertar_registro_accion(nombre_usuario, modulo, nombre_accion, descripcion, ip_usuario, user_agent, browser_id):
    nuevo_registro = TRegistroAccionesModulo(
        NombreUsuario=nombre_usuario,
        Modulo=modulo,
        NombreAccion=nombre_accion,
        FechaHora=timezone.now(),  # Asigna la fecha y hora actual
        Descripcion=descripcion,
        IpUsuario=ip_usuario,
        UserAgent=user_agent,
        BrowserId=browser_id
    )
    
    nuevo_registro.save()
    imprimir(nuevo_registro)
    
def get_client_ip(request):
    """
    Intenta obtener la dirección IP real del cliente a partir de una solicitud HTTP en Django.
    Esta función tiene en cuenta cabeceras comunes utilizadas por proxies y balanceadores de carga.
    """
    # Lista de posibles cabeceras HTTP que pueden contener la dirección IP real
    ip_headers = [
        'HTTP_X_FORWARDED_FOR',  # Usual en configuraciones con proxies
        'HTTP_X_REAL_IP',        # Usual con ciertos servidores/proxies, como Nginx
        'HTTP_CLIENT_IP',        # Otra posible cabecera con la IP del cliente
        'HTTP_X_FORWARDED',      # Otra cabecera de proxy
        'HTTP_X_CLUSTER_CLIENT_IP',  # Cabecera utilizada por algunos balanceadores de carga
        'HTTP_FORWARDED_FOR',    # Otra variante de la cabecera FORWARDED_FOR
        'HTTP_FORWARDED'         # Versión simplificada de la cabecera FORWARDED
    ]

    # Intentar obtener la IP desde las cabeceras definidas
    for header in ip_headers:
        ip = request.META.get(header)
        if ip:
            # En algunos casos, la cabecera puede contener múltiples IPs,
            # entonces se toma la primera que generalmente es la del cliente
            ip = ip.split(',')[0].strip()
            if ip:
                return ip

    # Si no se encuentra en las cabeceras, tomar la dirección del remitente de la solicitud
    return request.META.get('REMOTE_ADDR')