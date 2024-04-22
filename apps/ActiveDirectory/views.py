from django.shortcuts import render , redirect, get_object_or_404
from django.conf import settings
from ldap3 import Server, Connection, ALL_ATTRIBUTES , MODIFY_REPLACE , ALL , NTLM
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
import re
import time
from cryptography.fernet import Fernet
from apps.AsignarUsuario.models import VallEmpleado, TRegistroAccionesModulo ,VAllReclutamiento
from .models import TActiveDirectoryIp
from apps.RegistroModulo.models import TRegistroDeModulo
from .utils import AtributosDeEmpleado , IPSinBaseDatos
from django.contrib.auth.models import User
import json
import os
from django.db.models import Q
from datetime import datetime
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

ENCRYPTION_KEY_DESCRIPCION =os.environ.get('KEY_DESCRIPCION').encode()
ENCRYPTION_KEY_NOMBRE = os.environ.get('KEY_NOMBRE').encode()
def es_superusuario(user):
    return user.is_authenticated and user.is_superuser

empleado = AtributosDeEmpleado()
ip_sin_base_dato = IPSinBaseDatos().cambiar_ip('192.192.194.10') #en caso que no funcione la base datos




#CONFIGURACION PARA EL IP DEL SERVIDOR AD -------------------------------------------------------
def asignar_ip():
    
     # Determina el servidor basado en el entorno
    servidor = 'ADVirtual' if settings.DEBUG else 'ADProduccion'
    # imprimir(servidor )
    # Realiza la consulta una sola vez usando la variable `servidor`
    ip = TActiveDirectoryIp.objects.filter(server=servidor).first()
    #imprimir(ip.ip)
    return ip #if ip else ip_sin_base_dato  

def asignar_dominio():
    if settings.DEBUG:
        dominio='OU=UsersIAI,DC=iai,DC=com,DC=mx' #dominio de AD para el desarrollo 
        dominioRaiz='DC=iai,DC=com,DC=mx'
    else:
        dominio='OU=UsersIAI,DC=iai,DC=com,DC=mx'# dominio de AD  para produccion 
        dominioRaiz='DC=iai,DC=com,DC=mx'

    dominios={
        'dominio':dominio,
        'dominioRaiz':dominioRaiz
    }
    return dominios

def obtener_servidor_ad():
    ip_dinamica = asignar_ip().ip
    servidorAD = f'{settings.AD_SERVER}{ip_dinamica}'
    return servidorAD

#FIN DE CONFIGURACION PARA EL IP DEL SERVIDOR AD -------------------------------------------------------

# crea las variables de domino 
domino=asignar_dominio()['dominio']
dominoRaiz=asignar_dominio()['dominioRaiz']

unidadOrganizativa = ('OU=Bajas','OU=Administracion','OU=Ingeniería','OU=DCASS','OU=Proyectos Especiales','0') #esta variable esta relacionada con las funciones de   mover_usuario_ou y asignar_Departamento
selectDepartamento= ('Administración','Ingeniería','Calidad, Ambiental, Seguridad y Salud','Proyectos Especiales','Tecnatom','Presidencia Grupo IAI')

def SelectDepartamento():
    return selectDepartamento


def asignar_Departamento(departamento):
    
    if departamento == "Administración":
        opc = 1
    elif departamento == "Ingeniería":
        opc = 2
    elif departamento == "Calidad, Ambiental, Seguridad y Salud":
        opc = 3
    elif departamento == "Proyectos Especiales":
        opc = 4
    else:
        opc = 5 #se le va asignar  '0'
    return opc


def actualizar_empleados():
    users = VallEmpleado.objects.exclude(username__isnull=True).exclude(username='')
    usuarios_modificados = []
    no_cambios = True

    for usuario in users:
        try:
            with connect_to_ad() as conn:
                search_base = domino
                search_filter = f'(sAMAccountName={usuario.username})'
                conn.search(search_base, search_filter, attributes=['sAMAccountName', 'userAccountControl', 'physicalDeliveryOfficeName', 'department','title'])
                if conn.entries:
                    dn = conn.entries[0].entry_dn
                    AccountControl_actual = conn.entries[0].userAccountControl.value
                    physicalDeliveryOfficeName_actual = conn.entries[0].physicalDeliveryOfficeName.value
                    department_actual = conn.entries[0].department.value
                    puesto_actual = conn.entries[0].title.value
                    imprimir(dn)
                    if (physicalDeliveryOfficeName_actual.strip().lower() != usuario.Proyecto.strip().lower() or
                            department_actual.strip().lower() != usuario.nombre_direccion.strip().lower() or puesto_actual.strip().lower() != usuario.Nombre_ct.strip().lower()):
                        imprimir("")
                        imprimir("*****************************************************************************************")
                        imprimir(dn)
                        imprimir(physicalDeliveryOfficeName_actual)
                        imprimir( department_actual)
                        imprimir( puesto_actual)
                        imprimir("*****************************************************************************************")
                        imprimir("")
                        
                        
                        
                        
                        
                        changes = {
                            'physicalDeliveryOfficeName': [(MODIFY_REPLACE, [usuario.Proyecto])],
                            'department': [(MODIFY_REPLACE, [usuario.nombre_direccion])],
                            'title': [(MODIFY_REPLACE, [usuario.Nombre_ct])]
                        }
                        conn.modify(dn, changes)
                        imprimir("****************if conn.result['result'] == 0:*************************************************************************")
                        if conn.result['result'] == 0:
                            usuarios_modificados.append(usuario)
                            insertar_registro_accion(
                                "DJANGO",
                                'Modulo AD',
                                'Actualizo',
                                f"Se Actualizó  proyecto({physicalDeliveryOfficeName_actual} -> {usuario.Proyecto}) y direccion({department_actual}->{usuario.nombre_direccion}) del '{usuario.username}' en Active Directory ",
                                '0.0.0.0',
                                "LOCALHOST",
                                'N/A'
                                )
                            if AccountControl_actual != 66050:
                                imprimir(mover_usuario_ou_sys(usuario.username, unidadOrganizativa[asignar_Departamento(usuario.nombre_direccion)]))
                            
                            no_cambios = False
        except Exception as e:
            imprimir(f"Error al actualizar en Active Directory: {str(e)}")

    if no_cambios:
        imprimir("No se realizó ningún cambio necesario.")
        
    return usuarios_modificados



def mover_usuario_ou_sys(nombre_usuario, nueva_ou):
    mensaje = None
    try:
        with connect_to_ad() as conn:
            # Buscar el Distinguished Name (DN) actual del usuario
            search_filter = f'(sAMAccountName={nombre_usuario})'
            conn.search(search_base=domino, search_filter=search_filter, attributes=['distinguishedName'])

            if conn.entries:
                dn_actual = conn.entries[0].distinguishedName.value
                #imprimir(f"DN actual: {dn_actual}")

                # Construir el nuevo DN
                nuevo_rdn = f"CN={nombre_usuario}"
                if (nueva_ou =='0'):
                    nueva_ou_completa = f"{domino}"
                else:    
                    nueva_ou_completa = f"{nueva_ou},{domino}"
                
                imprimir(f"Nuevo DN: {nuevo_rdn}, en OU: {nueva_ou_completa}")

                # Mover el usuario a la nueva OU
                conn.modify_dn(dn_actual, nuevo_rdn, new_superior=nueva_ou_completa)
                
                if conn.result['result'] == 0:
                    mensaje = 'Usuario movido correctamente.'
                    insertar_registro_accion(
                    "DJANGO",
                    'Modulo AD',
                    'Mover',
                    f"El usuario  '{nombre_usuario}' ha sido trasladado  a la nueva ubicación : {extraer_unidad_organizativa(nueva_ou_completa)[0]}",
                    '0.0.0.0',
                    "LOCALHOST",
                    'N/A'
                    )
                else:
                    mensaje = f"Error al mover usuario {conn.result['result']} :  {obtener_mensaje_error_ad(conn.result['result'])}"
            else:
                mensaje = "Usuario no encontrado en AD."
    except Exception as e:
        mensaje = f"Error al conectar con AD o al realizar la operación: {e}"

    return mensaje









@login_required
@user_passes_test(es_superusuario) # Solo permitir a superusuarios
def actualizarProyectoDireccion(request):

    users = VallEmpleado.objects.exclude(username__isnull=True).exclude(username='')
    
    #actualizar_empleados()
    usuariosmodificados = []  # Lista para almacenar los usuarios modificados
    usuariosmodificados = actualizar_empleados()
    """
    noCambios=True
    for usuario in users:
            try:
                with connect_to_ad() as conn:
                    search_base = domino
                    search_filter = f'(sAMAccountName={usuario.username})'  # Asumiendo sAMAccountName como identificador
                    conn.search(search_base, search_filter, attributes=['sAMAccountName','userAccountControl','physicalDeliveryOfficeName','department','title'])
                    if conn.entries:
                        dn = conn.entries[0].entry_dn
                        AccountControl_actual = conn.entries[0].userAccountControl.value
                        physicalDeliveryOfficeName_actual = conn.entries[0].physicalDeliveryOfficeName.value
                        department_actual = conn.entries[0].department.value
                        puesto_actual = conn.entries[0].title.value

                        imprimir(dn)
                       
                        if physicalDeliveryOfficeName_actual.strip().lower() != usuario.Proyecto.strip().lower() or department_actual.strip().lower() != usuario.nombre_direccion.strip().lower() or puesto_actual.strip().lower() != usuario.Nombre_ct.strip().lower() :
                            imprimir("")
                            imprimir("*****************************************************************************************")
                            imprimir(dn)
                            imprimir(physicalDeliveryOfficeName_actual)
                            imprimir( department_actual)
                            imprimir( puesto_actual)
                            imprimir("*****************************************************************************************")
                            imprimir("")
                            changes = {
                                'physicalDeliveryOfficeName': [(MODIFY_REPLACE, [usuario.Proyecto])],
                                'department': [(MODIFY_REPLACE, [usuario.nombre_direccion])],
                                'title': [(MODIFY_REPLACE, [usuario.Nombre_ct])],
                            }
                            conn.modify(dn, changes)
                            if conn.result['result'] == 0:  # Si la operación fue exitosa
                                insertar_registro_accion(
                                    empleado.nameUser(request), 'Modulo AD',
                                    'Actualizar',
                                    f"Se Actualizó  proyecto({physicalDeliveryOfficeName_actual} -> {usuario.Proyecto}) y direccion({department_actual}->{usuario.nombre_direccion}) del '{usuario.username}' en Active Directory ",
                                    get_client_ip(request),
                                    request.META.get('HTTP_USER_AGENT'),
                                    'N/A'
                                    )
                                usuariosmodificados.append(usuario)  # Añade el nombre de usuario a la lista                               
                                if AccountControl_actual !=66050: 
                                    imprimir(mover_usuario_ou(usuario.username, unidadOrganizativa[asignar_Departamento(usuario.nombre_direccion)],request))  # no comentar esta linea XD
                                    #imprimir(f" **************numero : {AccountControl_actual}") 
                                    
                                messages.success(request, f" {obtener_mensaje_error_ad(conn.result['result'])}")
                                noCambios=False
                            else:
                                messages.error(request,  f"Error al actualizar {usuario.username} en Active Directory.  {conn.result['result']} :  {obtener_mensaje_error_ad(conn.result['result'])}")
                                
                        else:
                           if noCambios:
                              messages.info(request, f"No se realizo ningun cambio necesario .")
            except Exception as e:
                messages.error(request,f"Error al actualizar en Active Directory: {str(e)}" )  # Considera usar logging
        """
       
    #cn --------->usuario.username
    # physicalDeliveryOfficeName  ----> usuario.Proyecto
    # department --------->  usuario.nombre_direccion

   
    encabezados ={
        'title' :' Actualizar Proyecto y Dirección del Personal de Grupo IAI',
        'Encabezado' :'Actualización Proyecto y Dirección  del Personal de Grupo IAI',
        'SubEncabezado' :'',
        'EncabezadoNav' :'Actualizar Proyecto y Dirección ',
        'EncabezadoCard' : 'Empleados Actualizados del atributo Proyecto y Dirección ',
       
        
    }
   # print(empleados)
    context = {
        'active_page': 'usuarios',
        'nombre_usuario': empleado.nameUser(request),
        'foto':empleado.photoUser(request),
        'Categoria': empleado.Categoria(request),
        'encabezados' :encabezados,
        'users':usuariosmodificados
        
    }




    return render(request, 'actualizarProyectoDireccion.html',context)








@login_required
@user_passes_test(es_superusuario) # Solo permitir a superusuarios
def personalNoContratada(request):
   
    #upper() para mayuscula 
    #strip() para quitar los espacios en blanco que se encuentra al principio o al final de la cadena 
    #lower(): Convierte todos los caracteres de la cadena a minúsculas.
    #title(): Convierte la primera letra de cada palabra en una cadena a mayúscula.
    #capitalize(): Convierte la primera letra de la cadena a mayúscula y el resto a minúsculas
    # Aquí la lógica para mostrar la página de inicio
    if request.method == 'POST':
        nombre_usuario = request.POST['nombre_usuario'].lower().strip()
        nombre_pila = request.POST['nombre_pila'].strip().title()
        apellido = request.POST['apellido'].strip().title()
        nombre_completo = request.POST['nombre_completo'].strip().title()
        email = request.POST['email'].lower().strip()
        password = request.POST['password'].strip()
        nombre_inicio_sesion = request.POST['nombre_inicio_sesion'].lower().strip()
        departamento = request.POST['departamento'].strip()
        puesto = request.POST['puestoCT'].strip()
        proyecto =request.POST['nameProyecto'].strip()
        #imprimir( nombre_usuario,nombre_pila,apellido,nombre_completo,email,password,nombre_inicio_sesion,departamento,puesto )
        dominio_Principal ='@'+'.'.join(part.replace('DC=', '') for part in domino.split(',') if part.startswith('DC=')) 
        quoted_password = f'"{password}"'.encode('utf-16-le')
        LugarCreado=" "
        LugarNoCreado=" "
        
        
        
        
        #if usuarioexisteIDIAI(nombre_usuario): 
      #  if existeUsuario(nombre_usuario) : #VERIFICA SI EXISTE USUARIO EN ACTIVE DIRECTORY <---AQUÍ ESTUVO SON GOKU XD
        if existeUsuario(nombre_usuario) :
            LugarNoCreado+="Active Directory "
            messages.error(request,f"Usuario existente en {LugarNoCreado}: {nombre_usuario}")
            imprimir(f"Usuario existente en {LugarNoCreado}: {nombre_usuario}")
            
        else:              
            try:
                    #server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
                with connect_to_ad() as conn:
                        
                    #user_dn = f"CN={nombre_usuario},CN=Users,DC=iai,DC=com,DC=mx"
                    #user_dn = f"CN={nombre_usuario},OU=iaiUsuario,OU=RedGrupoIAI,{domino}"
                    user_dn = f"CN={nombre_usuario},{unidadOrganizativa[asignar_Departamento(departamento)]},{domino}"
                    conn.add(user_dn, ['top', 'person', 'organizationalPerson', 'user'], {
                            'cn': nombre_usuario,
                            'givenName':nombre_pila,
                            'sn':apellido,
                            'mail':email,
                            'displayName': nombre_completo,
                            'sAMAccountName':nombre_inicio_sesion,
                        # 'sAMAccountType':805306368,
                            'userPrincipalName':nombre_inicio_sesion+dominio_Principal,
                            'department':departamento,
                            'title':puesto,
                            'userPassword': quoted_password,
                            'unicodePwd':quoted_password, #este linea guarda la contraseña en AD PERO DEBE CUMPLIR CON LAS CODICIONES DE SSL EN EL SERVIDOR WEB Y EL SEVIDOR AD CON EL PUERTO 636
                            #'userAccountControl':'512', # Habilita la cuenta
                            'physicalDeliveryOfficeName'  : proyecto,
                            # ... otros atributos
                    })
                        # Verificar el resultado de la creación del usuario
                    
                    
                    
                    if conn.result['result'] == 0:  # éxito
                        LugarCreado+="Active Directory, "
                        messages.success(request, f'Usuario creado correctamente en {LugarCreado}.')
                        imprimir(f"Usuario creado en {LugarCreado}:{nombre_usuario}")
                        #codigo para guardar en la bitacora -------
                        
                        mensajeCont =f"El usuario '{nombre_usuario}' de {nombre_completo} fue creado en Active Directory"
                        insertar_registro_accion(
                            empleado.nameUser(request),
                            'Modulo AD',
                            'Crear',
                            mensajeCont,
                            get_client_ip(request),
                            request.META.get('HTTP_USER_AGENT'),
                            'N/A'
                            )
                        notificacionCorreo(request,f'Active Directory Creación del usuario {nombre_usuario}','Creación de usuario',mensajeCont)    
                            #return redirect('usuariosID')
                            
                            
                    else:
                        messages.error(request, f"Error {conn.result['result']} :  {obtener_mensaje_error_ad(conn.result['result'])}")
                        return redirect('personalNoContratada') 
                        
                            #return redirect('usuariosID')
                            
            except Exception as e:
                messages.error(request, f"Error al conectar con AD: {str(e)}")
                return redirect('personalNoContratada') 
        
        
        
        
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
            LugarCreado+=" IDIAI V2 "
            n = Fernet(ENCRYPTION_KEY_NOMBRE)
            f = Fernet(ENCRYPTION_KEY_DESCRIPCION)
            nombre_cifrado = n.encrypt(nombre_usuario.encode().strip()).decode()
            descripcion_cifrado = f.encrypt(password.encode()).decode()
            nombreCompleto = nombre_completo
            messages.success(request,f"Usuario creado en  {LugarCreado} :{nombre_usuario}") # 
            imprimir(f"Usuario creado en {LugarCreado}:{nombre_usuario}")
            
            mensajeCont =f"El usuario '{nombre_usuario}' de {nombre_completo} fue creado en IDIAI V2"
            insertar_registro_accion(
                            empleado.nameUser(request),
                            'Modulo AD',
                            'Crear',
                            mensajeCont,
                            get_client_ip(request),
                            request.META.get('HTTP_USER_AGENT'),
                            'N/A'
                            )         

            notificacionCorreo(request,f'IDIAI V2 creación del usuario {nombre_usuario}','Creación de usuario',mensajeCont)
            nuevo_usuario, created2 = TRegistroDeModulo.objects.get_or_create(
                _nombre=nombre_cifrado,
                defaults={
                    '_descripcion': descripcion_cifrado, 'nombre_completo':nombreCompleto,
                    
                }
            )
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
                 
            return redirect('personalNoContratada') 
            
            
            
        else:
            LugarNoCreado+= ' IDIAI V2 y Modulo '
            messages.error(request,f"Usuario existente en {LugarNoCreado}: {nombre_usuario}")
            return redirect('personalNoContratada') 
        
    
        
    
    empleados = []
    empleados = VAllReclutamiento.objects.all()
    encabezados ={
        'title' :'Personal en reclutamiento de Grupo IAI',
        'Encabezado' :'Personal en reclutamiento  de Grupo IAI',
        'SubEncabezado' :'Plataforma para Agregar  usuarios a  Active Directory',
        'EncabezadoNav' :'Agregar',
        'EncabezadoCard' : 'Agregar Usuario    Active Directory',
        'titulomodal1':'Crear Usuario de Active Directory'
        
    }
   # print(empleados)
    context = {
        'empleados' : empleados,
        'usersAdmin': empleados.filter( nombre_direccion='Administración'),
        'usersIng': empleados.filter( nombre_direccion='Ingeniería'),
        'usersDCASS': empleados.filter( nombre_direccion='Calidad, Ambiental, Seguridad y Salud'),
        'usersPS': empleados.filter( nombre_direccion='Proyectos Especiales'),
        'active_page': 'ADsolicitud',
        'nombre_usuario': empleado.nameUser(request),
        'foto':empleado.photoUser(request),
        'Categoria': empleado.Categoria(request),
        'encabezados' :encabezados,
        'ActiveDirectory' :True,
        'selectDepartamento': selectDepartamento
    }
    return render(request, 'nuevoPersonal.html',context)




@login_required
@user_passes_test(es_superusuario) # Solo permitir a superusuarios
def ipconfig(request): #vista para la gestion de la ip de AD
    ip=None
    
    encabezados ={
        'title' :'IP configuración ',
        'Encabezado' :'Configuración de la IP de Active Directory',
        'SubEncabezado' :'',
        'EncabezadoNav' :'IP Configuracion ',
        'EncabezadoCard' : 'Introduce la nueva IP',
        
    }
   
    if request.method == 'POST':
        action = request.POST.get('action')
        nueva_ip = request.POST['ip'].strip()
        registro_id = request.POST.get('id')
        #imprimir(action)
        if action == 'probar':
            # Aquí va la lógica para probar la conexión LDAP
            # la  función llamada `probar_conexion_ldap` que devuelve True si la conexión es exitosa
            exitosa = probar_conexion_LDAP(request,nueva_ip)
            if exitosa:
                time.sleep(5)
                messages.success(request, "La conexión LDAP con la IP {} ha sido exitosa.".format(nueva_ip))
            else:
                imprimir(exitosa)
                #messages.error(request, "Error al conectar con LDAP usando la IP {}.".format(nueva_ip))
                
        elif action == 'guardar':
            # Aquí va la lógica para guardar la IP actualizada en la base de datos
            # Expresión regular para validar la dirección IP
            #imprimir('entro aqui XD')
            insertar_registro_accion(
                empleado.nameUser(request),
                'Modulo AD',
                'IP',
                f"Se a modificado la IP de '{asignar_ip().server}', IP anterior {asignar_ip().ip}: IP Nueva : {nueva_ip}",
                get_client_ip(request),
                request.META.get('HTTP_USER_AGENT'),
                'N/A'
            
            )
            ip_regex = r'^(\d{1,3}\.){3}\d{1,3}$'  #0.0.0.0
        
            if not registro_id:
                time.sleep(5)
                messages.error(request, "ID del registro no proporcionado.")
                return redirect('ipconfig')

            # Intenta obtener el registro específico por ID
            registro = get_object_or_404(TActiveDirectoryIp, id=registro_id)

            # Verifica si 'nueva_ip' no está vacía
            if nueva_ip : # and re.match(ip_regex, nueva_ip):
                registro.ip = nueva_ip  # Actualiza el campo 'ip' del registro
                time.sleep(5)
                registro.save()  # Guarda los cambios en la base de datos
                time.sleep(10)
                messages.success(request, "Registro actualizado exitosamente.")
                return redirect('ipconfig')
            else:
                # Maneja el caso en que 'nueva_ip' esté vacía
                time.sleep(5)
                messages.error(request, "La nueva IP no puede estar vacía")# y debe tener un formato válido (0.0.0.0).")
                return redirect('ipconfig')
        
  
    
    ip=asignar_ip()
    
    context = {
        'active_page': 'ipconfig',
        'nombre_usuario':empleado.nameUser(request),
        'ip' : ip,
        'foto':empleado.photoUser(request),
        'encabezados' :encabezados,
        'Categoria': empleado.Categoria(request)
    }
    return render(request,'ipconfig.html',context)



@login_required
@user_passes_test(es_superusuario) # Solo permitir a superusuarios  
def bitacora(request): #LA BITACORA QUE LLEVA EL SISTEMAS DE AD PARA LLEVAR EL HISTORICO DE LOS PROCESOS QUE SE REALIZA EN LA INTERFAZ
    mensaje=None
    
    encabezados ={
        'title' :'Bitácora AD',
        'Encabezado' :'Bienvenido a la bitácora de  Active Directory:',
        'SubEncabezado' :'Su plataforma para visualizar las acciones.',
        'EncabezadoNav' :'Bitácora AD',
        'EncabezadoCard' : 'Registros de Acciones',
        
    }
    #registros= TRegistroAccionesModulo.objects.all()
    registros = TRegistroAccionesModulo.objects.filter(Modulo='Modulo AD').order_by('-FechaHora')[:1000] # solo muestra los ultimos  mil registros 
    context = {
                    'active_page': 'bitacora',
                    'nombre_usuario': empleado.nameUser(request),
                    'mensaje': mensaje,
                    'registros':registros,
                    'foto':empleado.photoUser(request),
                    'encabezados' :encabezados,
                    'Categoria': empleado.Categoria(request)
                    }
        
    
    
    return render(request, 'bitacora.html',context)


@login_required
@user_passes_test(es_superusuario) # Solo permitir a superusuarios 
def consultarUsuariosIDIAI(request):
    mensaje = None
    opc = 0
    
    imprimir(f"Unidades Organizativas de AD :  {obtenerUnidadesOrganizativas()}")
    
    # Obtiene los usuarios de la base de datos
    usuarios = VallEmpleado.objects.exclude(username__isnull=True).exclude(username='').exclude(is_active=False)
    UsuaruisDown = VallEmpleado.objects.exclude(username__isnull=True).exclude(username='').exclude(is_active=True)
   
    
    
    
    # Verifica la existencia en AD para cada conjunto de usuarios y agrega la información al contexto
    for conjunto_usuarios in [usuarios,UsuaruisDown]:
        for usuario in conjunto_usuarios:
            # Suponiendo que 'username' es el campo relevante para verificar en AD
            #usuario.existe_en_ad = existeUsuario(usuario.username) # lo quite porque era tardado verificar todos XD
            usuario.existe_en_ad = True
    
    
    usuariosAdmin =usuarios.filter(nombre_direccion="Administración")  
    usuariosIng = usuarios.filter(nombre_direccion="Ingeniería")
    usuariosDCASS =usuarios.filter(nombre_direccion="Calidad, Ambiental, Seguridad y Salud")
    UsuariosPS =usuarios.filter(nombre_direccion="Proyectos Especiales")

    
     
    


    if request.method == 'POST':
        dominio_Principal ='@'+'.'.join(part.replace('DC=', '') for part in domino.split(',') if part.startswith('DC='))
        nombre_usuario = request.POST['nombre_usuario'].lower().strip()
        nombre_pila = request.POST['nombre_pila'].strip().title()
        apellido = request.POST['apellido'].strip().title()
        nombre_completo = request.POST['nombre_completo'].strip().title()
        email = request.POST['email'].lower().strip()
        password = request.POST['password']
        nombre_inicio_sesion = request.POST['nombre_inicio_sesion'].lower().strip()
        departamento = request.POST['departamento'].strip()
        puesto = request.POST['puesto'].strip()
        proyecto =request.POST['nameProyecto'].strip()
        # ... otros campos
        #imprimir(password)
        # Preparar la contraseña en formato adecuado para AD
        quoted_password = f'"{password}"'.encode('utf-16-le')
        #imprimir(quoted_password )
        # Establecer conexión con Active Directory
        try:
            #server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
            with connect_to_ad() as conn:
                
                #user_dn = f"CN={nombre_usuario},CN=Users,DC=iai,DC=com,DC=mx"
                 #user_dn = f"CN={nombre_usuario},OU=iaiUsuario,OU=RedGrupoIAI,{domino}"
                user_dn = f"CN={nombre_usuario},{unidadOrganizativa[asignar_Departamento(departamento)]},{domino}"
                conn.add(user_dn, ['top', 'person', 'organizationalPerson', 'user'], {
                    'cn': nombre_usuario,
                    'givenName':nombre_pila,
                    'sn':apellido,
                    'mail':email,
                    'displayName': nombre_completo,
                    'sAMAccountName':nombre_inicio_sesion,
                   # 'sAMAccountType':805306368,
                    'userPrincipalName':nombre_inicio_sesion+dominio_Principal,
                    'department':departamento,
                    'title':puesto,
                   'userPassword': quoted_password,
                   'unicodePwd':quoted_password, #este linea guarda la contraseña en AD PERO DEBE CUMPLIR CON LAS CODICIONES DE SSL EN EL SERVIDOR WEB Y EL SEVIDOR AD CON EL PUERTO 636
                    #'userAccountControl':'512', # Habilita la cuenta
                   'physicalDeliveryOfficeName'  : proyecto,
                    # ... otros atributos
                })
                # Verificar el resultado de la creación del usuario
                if conn.result['result'] == 0:  # éxito
                    messages.success(request, 'Usuario creado correctamente.')
                    mensaje = {'titulo': 'Éxito', 'texto': 'Usuario creado correctamente', 'tipo': 'success'}
                    #codigo para guardar en la bitacora -------
                    
                    mensajeCont =f"El usuario '{nombre_usuario}' de {nombre_completo} fue creado en Active Directory"
                    insertar_registro_accion(
                    empleado.nameUser(request),
                    'Modulo AD',
                    'Crear',
                     mensajeCont,
                    get_client_ip(request),
                    request.META.get('HTTP_USER_AGENT'),
                    'N/A'
                    )
                    
                    #return redirect('usuariosID')
                    
                    notificacionCorreo(request,f'Active Directory Creación del usuario {nombre_usuario}','Creación de usuario',mensajeCont)
                else:
                    messages.error(request, f"Error {conn.result['result']} :  {obtener_mensaje_error_ad(conn.result['result'])}")
                    mensaje = {'titulo': 'Error', 'texto': f"Error {conn.result['result']} :  {obtener_mensaje_error_ad(conn.result['result'])}", 'tipo': 'error'}
                    imprimir(mensaje)
                    #return redirect('usuariosID')
        except Exception as e:
            messages.error(request, f"Error al conectar con AD: {str(e)}")
            mensaje = {'titulo': 'Error', 'texto': f'Excepción: {str(e)}', 'tipo': 'error'}
            imprimir(mensaje)
            return redirect('usuariosID')
    
    context = {
                    'active_page': 'usuariosID',
                    'nombre_usuario': empleado.nameUser(request),
                    'users': usuarios,
                    'usersDown' : UsuaruisDown,
                    'usersAdmin': usuariosAdmin,
                    'usersIng': usuariosIng,
                    'usersDCASS':usuariosDCASS,
                    'usersPS':UsuariosPS,
                    'mensaje': mensaje,
                    'foto':empleado.photoUser(request),
                    'Categoria': empleado.Categoria(request),
                    'selectDepartamento': selectDepartamento
                    }
        
    
    
    return render(request, 'UsuariosIDIAI.html',context)



@login_required
@user_passes_test(es_superusuario) # Solo permitir a superusuarios
def consultar_usuarios(request): #Consulta los usuarios de Active Directory 
    encabezados ={
        'title' :'Activate Directory',
        'Encabezado' :'Bienvenido a Active Directory:',
        'SubEncabezado' :'Su plataforma para visualizar  y editar usuarios.',
        'EncabezadoNav' :'Consulta',
        'EncabezadoCard' : 'Usuarios de Activate Directory',
        
    }
    usuarios = []
    usuariosAdmin =[]
    usuariosIng = []
    usuariosDCASS =[]
    UsuariosPS =[]
    UsuaruisDown=[]
    try:
        
        with connect_to_ad() as connection:# Establece la conexión con el servidor de Active Directory
            search_base = domino #dominoRaiz
            search_filter = '(objectClass=user)'
            
            attributes = ['cn', 
                          'sn', 
                          'givenName', 
                          'userPrincipalName', 
                          'mail', 
                          'displayName', 
                          'sAMAccountName', 
                          'distinguishedName', 
                          'physicalDeliveryOfficeName', 
                          'description',
                          'department',
                          'title',
                          'userAccountControl'
                          ]
            
            connection.search(search_base, search_filter, attributes=attributes)
            for entry in connection.entries:
                domain_name = '.'.join(part.replace('DC=', '') for part in entry.distinguishedName.value.split(',') if part.startswith('DC='))
                
                useraccountcontrol_str = entry.userAccountControl.value if 'userAccountControl' in entry else '0'
                usuario = {
                    'nombre': entry.cn.value if 'cn' in entry else None,
                    'apellidos': entry.sn.value if 'sn' in entry else None,
                    'nombre_de_pila': entry.givenName.value if 'givenName' in entry else None,
                    'nombre_completo': entry.displayName.value if 'displayName' in entry else None,
                    'correo': entry.mail.value if 'mail' in entry else None,
                    'usuario_principal': entry.userPrincipalName.value if 'userPrincipalName' in entry else None,
                    'nombre_inicio_sesion': entry.sAMAccountName.value if 'sAMAccountName' in entry else None, 
                    'nombre_dominio':domain_name, #entry.distinguishedName.value if 'distinguishedName' in entry else None, 
                    'nproyecto': entry.physicalDeliveryOfficeName.value if 'physicalDeliveryOfficeName' in entry else None,
                    'descripcion': entry.description.value if 'description' in entry else None,
                    'departamento': entry.department.value if 'department' in entry else None,  # Nuevo atributo
                    'puesto': entry.title.value if 'title' in entry else None,  # Nuevo atributo
                    'userAccountControl': entry.userAccountControl.value if 'userAccountControl' in entry else None,
                    'esta_deshabilitado': is_account_disabled(useraccountcontrol_str),
                    'DistinguishedName' : entry.distinguishedName.value if 'DistinguishedName' in entry else None,
                    
                }

                #imprimir( entry.distinguishedName.value)
                #if 'cn' in entry and entry.cn.value.lower() != 'administrador':
                if not is_account_disabled(useraccountcontrol_str):
                    usuarios.append(usuario)

                if 'department' in entry:
                    if entry.department.value == 'Administración' and not is_account_disabled(useraccountcontrol_str):
                        usuariosAdmin.append(usuario)

                    elif entry.department.value == 'Ingeniería' and not is_account_disabled(useraccountcontrol_str):
                        usuariosIng.append(usuario)

                    elif entry.department.value == 'Calidad, Ambiental, Seguridad y Salud' and not is_account_disabled(useraccountcontrol_str):
                        usuariosDCASS.append(usuario)

                    elif entry.department.value == 'Proyectos Especiales' and not is_account_disabled(useraccountcontrol_str):
                        UsuariosPS.append(usuario)

                    elif is_account_disabled(useraccountcontrol_str):
                        UsuaruisDown.append(usuario)
                
                
                
    except Exception  as e:
        # Manejar la excepción, por ejemplo, registrando el error
        messages.error(request,f"Error al conectar o buscar en Active Directory: {str(e)}")
        imprimir(f"Error al conectar o buscar en Active Directory: {str(e)}")
    
    # Crear el diccionario de contexto con todas las variables necesarias
    context = {
        'users': usuarios,  # Lista de usuarios
        'usersAdmin': usuariosAdmin,
        'usersIng': usuariosIng,
        'usersDCASS':usuariosDCASS,
        'usersPS':UsuariosPS,
        'usersDown':UsuaruisDown,
        'active_page': 'usuarios',
        'nombre_usuario': empleado.nameUser(request),# Variable adicional
        'foto':empleado.photoUser(request),
        'encabezados' :encabezados,
        'Categoria': empleado.Categoria(request),
        'selectDepartamento': selectDepartamento,
        'tabUsuario':1 #talvez esto no funciones
        # Puedes agregar más variables aquí si lo necesitas
    }
    
    # imprimir(empleado.photoUser(request))
    # Renderiza la lista de usuarios en una plantilla HTML
    return render(request, 'Usuarios.html', context)



@login_required
@user_passes_test(es_superusuario) # Solo permitir a superusuarios
def editar_usuario(request):
    #imprimir("Vista de editar Usuario ")
    if request.method == 'POST':
         # Captura los datos enviados desde el formulario
        nombre_usuario = request.POST.get('nombre_usuario').lower().strip()
        nombre_pila = request.POST.get('nombre_pila').strip().title()
        apellido = request.POST.get('apellido').strip().title()
        nombre_completo = request.POST.get('nombre_completo').strip().title()
        email = request.POST.get('email').lower().strip()
        departamento = request.POST.get('departamento').strip()
        puesto = request.POST.get('puesto').strip()
        nombre_inicio_sesion = request.POST.get('nombre_inicio_sesion').lower().strip()
        user_dn = request.POST.get('distinguished_name').strip()
        proyecto =request.POST['nameProyecto'].strip()
        # ... otros campos ....
        #imprimir(nombre_usuario)
        #imprimir(user_dn)
        # Conectar a Active Directory
        insertar_registro_accion(
        empleado.nameUser(request),
        'Modulo AD',
        'Editar',
        f"Se han modificado los datos del usuario '{nombre_usuario}'  en AD ",
        get_client_ip(request),
        request.META.get('HTTP_USER_AGENT'),
        'N/A'
        )
        try:
            #server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
            with connect_to_ad() as conn:
             #   user_dn = f"CN={nombre_usuario},OU=iaiUsuario,OU=RedGrupoIAI,{domino}"
                
                # Actualizar los atributos
                conn.modify(user_dn, {
                    'givenName': [(MODIFY_REPLACE, [nombre_pila])],
                    'sn': [(MODIFY_REPLACE, [apellido])],
                    'displayName': [(MODIFY_REPLACE, [nombre_completo])],
                    'mail': [(MODIFY_REPLACE, [email])],
                    'department': [(MODIFY_REPLACE, [departamento])],
                    'title': [(MODIFY_REPLACE, [puesto])],
                    'sAMAccountName': [(MODIFY_REPLACE, [nombre_inicio_sesion])],
                    'physicalDeliveryOfficeName': [(MODIFY_REPLACE, [proyecto])],
                    # ... otros atributos ..
                })

                # Verificar resultado de la modificación
                if conn.result['result'] == 0:  # éxito
                    messages.success(request, 'Usuario editado correctamente.')
                    imprimir('Usuario editado correctamente.')
                    imprimir(user_dn)
                    imprimir(UsuarioActivoAD(user_dn))
                    if UsuarioActivoAD(user_dn) == True:
                        imprimir(mover_usuario_ou(nombre_inicio_sesion, unidadOrganizativa[asignar_Departamento(departamento)],request))
                else:
                    messages.error(request, f"Error al editar usuario: {obtener_mensaje_error_ad(conn.result['result'])}")
                    imprimir( f"Error al editar usuario: {obtener_mensaje_error_ad(conn.result['result'])}")
        except Exception as e:
            messages.error(request, f"Error al conectar con AD: {str(e)}")
            imprimir(f"Error al conectar con AD: {str(e)}")
    # Redireccionar de vuelta a la lista de usuarios
    
    
    return redirect('usuarios')

 

#@user_passes_test(es_superusuario) # Solo permitir a superusuarios
@login_required
def home(request):
   # Inicializa la variable que determina si el usuario es superusuario
    es_super = es_superusuario(request.user)
    
    # Pasar el contexto como un diccionario a la plantilla
    context = {'es_super': es_super}
    
    return render(request, 'home.html', context)

@login_required
@user_passes_test(es_superusuario) # Solo permitir a superusuarios 
def salir (request):
    logout(request)
    return redirect ('home')



@login_required
@user_passes_test(es_superusuario) # Solo permitir a superusuarios
def agregar_usuario(request): #Esta función o vista fue mantenida con la posibilidad de que se pueda necesitar en el futuro. Por favor, revisen cuidadosamente las variables, ya que el dominio ha sido modificado.
    mensaje=None
    if request.method == 'POST':
        dominio_Principal = '@'+'.'.join(part.replace('DC=', '') for part in domino.split(',') if part.startswith('DC='))
        nombre_usuario = request.POST['nombre_usuario']
        nombre_pila = request.POST['nombre_pila']
        apellido = request.POST['apellido']
        nombre_completo = request.POST['nombre_completo']
        email = request.POST['email']
        password = request.POST['password']
        nombre_inicio_sesion = request.POST['nombre_inicio_sesion']
        departamento = request.POST['departamento']
        puesto = request.POST['puesto']
        # ... otros campos
       
        # Preparar la contraseña en formato adecuado para AD
        quoted_password = f'"{password}"'.encode('utf-16-le')
        # Establecer conexión con Active Directory
        try:
            #server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
            with connect_to_ad() as conn:
                
                #user_dn = f"CN={nombre_usuario},CN=Users,DC=iai,DC=com,DC=mx"
                #user_dn = f"CN={nombre_usuario},OU=iaiUsuario,OU=RedGrupoIAI,{domino}"
                user_dn = f"CN={nombre_usuario},{unidadOrganizativa[asignar_Departamento(departamento)]},{domino}"
                conn.add(user_dn, ['top', 'person', 'organizationalPerson', 'user'], {
                    'cn': nombre_usuario,
                    'givenName':nombre_pila,
                    'sn':apellido,
                    'mail':email,
                    'displayName': nombre_completo,
                    'sAMAccountName':nombre_inicio_sesion,
                   # 'sAMAccountType':805306368,
                    'userPrincipalName':nombre_inicio_sesion+dominio_Principal,
                    'department':departamento,
                    'title':puesto,
                    'userPassword': password,
                    'unicodePwd':quoted_password,
                    #'userAccountControl':'546', # Habilita la cuenta
                   
                    # ... otros atributos
                })
                # Verificar el resultado de la creación del usuario
                if conn.result['result'] == 0:  # éxito
                    messages.success(request, 'Usuario creado correctamente.')
                    mensaje = {'titulo': 'Éxito', 'texto': 'Usuario creado correctamente', 'tipo': 'success'}
                    #codigo para guardar en la bitacora -------
                    insertar_registro_accion(
                    empleado.nameUser(request),
                    'Modulo AD',
                    'Crear',
                    f"El usuario '{nombre_usuario}' fue creado en AD",
                    get_client_ip(request),
                    request.META.get('HTTP_USER_AGENT'),
                    'N/A'
                    )
                    return redirect('agregar_usuario')
                else:
                    messages.error(request, f"Error al crear usuario {conn.result['result']} :  {obtener_mensaje_error_ad(conn.result['result'])}")
                    mensaje = {'titulo': 'Error', 'texto': f"Error al crear usuario {conn.result['result']} :  {obtener_mensaje_error_ad(conn.result['result'])}", 'tipo': 'error'}
                    imprimir(mensaje)
                    return redirect('agregar_usuario')
        except Exception as e:
            messages.error(request, f"Error al conectar con AD: {str(e)}")
            mensaje = {'titulo': 'Error', 'texto': f'Excepción: {str(e)}', 'tipo': 'error'}
            imprimir(mensaje)
            return redirect('agregar_usuario')
  # Crear el diccionario de contexto con todas las variables necesarias
    context = {
        'active_page': 'agregar_usuario', # Variable adicional para el boton del menu 
        'nombre_usuario': empleado.nameUser(request),
        'foto':empleado.photoUser(request),
        'Categoria': empleado.Categoria(request),
        'mensaje': mensaje
        # Puedes agregar más variables aquí si lo necesitas
    }          
    
    return render(request, 'AgregarUsuario.html',context)   
# -----------------------------------------------------------funciones que no son vistas -----------------------------------
def is_account_disabled(useraccountcontrol_str):
    DISABLED_ACCOUNT_BIT = 0x2
    try:
        # Convertir el valor a entero
        useraccountcontrol_value = int(useraccountcontrol_str)
        # Verificar si el bit de cuenta deshabilitada está activado
        return (useraccountcontrol_value & DISABLED_ACCOUNT_BIT) != 0
    except ValueError:
        # En caso de que el valor no sea un número, asumir que la cuenta no está deshabilitada
        return False
 
def existeUsuario(nombreUsuario):
    try:
       # server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
        with connect_to_ad() as conn:
            search_base = dominoRaiz  # Asegúrate de que domino está definido y es correcto.
            search_filter = f'(cn={nombreUsuario})'  # Filtro para buscar por Common Name
            conn.search(search_base, search_filter, attributes=['cn'])
            return len(conn.entries) > 0
    except Exception as e:
        imprimir(f"Error al buscar en Active Directory: {str(e)}")
        return False

def probar_conexion_LDAP(request,nueva_ip):
    if settings.DEBUG:
        protocolo='ldaps' #dominio de AD para el desarrollo  puedes cambiarlo a ldap pero debe tener el puerto 389
   
    else:
        protocolo='ldaps'# dominio de AD  para produccion 
        
    try:     
        server = Server(f'{protocolo}://{nueva_ip}', port=settings.AD_PORT,use_ssl=True, get_info=ALL_ATTRIBUTES)
        conn = Connection(server, user=settings.AD_USER, password=settings.AD_PASSWORD, auto_bind=True)
            
        # Intenta establecer la conexión
        conexion_exitosa = conn.bind()
            
        # Asegura que la conexión se cierre después del intento
        conn.unbind()

        return conexion_exitosa
    except Exception as e:
        # Manejo de cualquier error durante la conexión o la desvinculación
        messages.error(request, f"Error al conectar con el servidor LDAP usando la IP {nueva_ip}: {e}")
        return False
        
   

 
def activar_usuario(request, nombre_usuario):
    imprimir("entro a activar el usuario : "+str(nombre_usuario))
    try:
        #server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
        with connect_to_ad() as conn:
            #user_dn = f"CN={nombre_usuario},OU=iaiUsuario,OU=RedGrupoIAI,{domino}"
            user_dn = nombre_usuario;
            imprimir(user_dn)
            # Establecer userAccountControl a 512 para activar la cuenta
            conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]}) # debe activarse con el 512 pero eso lo vamos a dejar al ultimo ajajajajaj #26/02/2024 se logro hacer 
            if conn.result['result'] == 0:
                messages.success(request, 'Usuario activado correctamente.')
                imprimir(f'Usuario activado correctamente.{user_dn }')
                mover = buscar_usuario_por_dn(nombre_usuario)
                imprimir(mover_usuario_ou(mover['cn'], unidadOrganizativa[asignar_Departamento(mover['department'])],request))
                insertar_registro_accion(
                empleado.nameUser(request),
                'Modulo AD',
                'Alta',
                f"El usuario '{mover['cn']}' fue dado de alta en AD ",
                get_client_ip(request),
                request.META.get('HTTP_USER_AGENT'),
                'N/A'
                )
                return redirect('usuarios')
            else:
                messages.error(request, f"Error al activar usuario: {conn.result['description']}")
                imprimir(f"Error al activar usuario: {conn.result['description']}")
    except Exception as e:
        messages.error(request, f"Error al conectar con AD: {str(e)}")
        imprimir(f"Error al conectar con AD: {str(e)}")

    
    
    
 
def desactivar_usuario(request, nombre_usuario):
    imprimir("entro a desactivar al usuario :"+str(nombre_usuario))
    try:
       # server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
        with connect_to_ad() as conn:
            #user_dn = f"CN={nombre_usuario},OU=iaiUsuario,OU=RedGrupoIAI,{domino}"
            user_dn = nombre_usuario;
            
           # imprimir(user_dn)
            # Establecer userAccountControl a 66050 para desactivar la cuenta
            conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [66050])]})
            if conn.result['result'] == 0:
                messages.success(request, 'Usuario desactivado correctamente.')
                imprimir('Usuario desactivado correctamente.')
                mover = buscar_usuario_por_dn(nombre_usuario)
                #cn=mover['cn']
                #department=mover['department']
                #imprimir(cn)
                #imprimir(department)
                imprimir(mover_usuario_ou(mover['cn'], unidadOrganizativa[0],request))
                insertar_registro_accion(
                empleado.nameUser(request),
                'Modulo AD',
                'Baja',
                f"El usuario '{mover['cn']}' fue dado de baja en AD ",
                get_client_ip(request),
                request.META.get('HTTP_USER_AGENT'),
                'N/A'
                )
                
                return redirect('usuarios')
            else:
                messages.error(request, f"Error al desactivar usuario: {conn.result['description']}")
                imprimir(f"Error al desactivar usuario: {conn.result['description']}")
    except Exception as e:
        messages.error(request, f"Error al conectar con AD: {str(e)}")
        imprimir(f"Error al conectar con AD: {str(e)}")



def extraer_unidad_organizativa(dn):
    """
    Extrae la Unidad Organizativa (OU) de un Distinguished Name (DN) en Active Directory.

    :param dn: Distinguished Name como cadena de texto.
    :return: Lista de Unidades Organizativas.
    """
    partes = dn.split(',')
    unidades_organizativas = [parte.strip()[3:] for parte in partes if parte.startswith('OU=')]
    return unidades_organizativas




def connect_to_ad():
    
        # Inicializa la variable de conexión a None para poder verificar luego si fue establecida
    conn = None
    try:
        servidorAD = obtener_servidor_ad()
        server = Server(servidorAD, use_ssl=True, get_info=ALL)  # Asumiendo que quieres usar SSL
        conn = Connection(server, user=settings.AD_USER, password=settings.AD_PASSWORD, auto_bind=True)
        
        # Si la conexión es exitosa, devuelve la conexión
        return conn
    except Exception as e:
        # Si ocurre un error, imprime o logea el error
        imprimir(f"Error al conectar con AD: {str(e)}")  # Considera usar logging en lugar de print
        # Asegúrate de cerrar la conexión si fue parcialmente establecida antes del error
        if conn:
            conn.unbind()
        # Podrías decidir lanzar la excepción nuevamente o manejarla de alguna manera específica
        raise
    
    #servidorAD = obtener_servidor_ad()
    #imprimir(servidorAD)
    #server = Server(servidorAD, port=settings.AD_PORT,use_ssl=True, get_info=ALL_ATTRIBUTES)
    
    #return Connection(server, user=settings.AD_USER, password=settings.AD_PASSWORD, auto_bind=True)

def verificar_usuario(request, nombre_usuario):
    existe = existeUsuario(nombre_usuario)
    existeIDIAI = usuarioexisteIDIAI(nombre_usuario)
    imprimir(f'active directory : {existe} IDIAI V2: {existeIDIAI}')
    return JsonResponse({'existe': existe , 'existeIDIAI':existeIDIAI}) 

@login_required  
@require_http_methods(["POST"])  # Asegurar que esta vista solo acepte solicitudes POST
def key_usuario(request):
    # Extraer el cuerpo de la solicitud y convertirlo de JSON a un diccionario de Python
    datos = json.loads(request.body)
    nombre_usuario = datos.get('nombre_usuario')
    nombre_completo = datos.get('nombre_completo')
    imprimir("Datos que recibe del POST :")
    imprimir(f'Nombre de Usuario:{nombre_usuario} : Nombre Completo:{nombre_completo}')
    
    # Paso 1: Filtrar por 'nombre_completo'
    registros_filtrados_por_nombre_completo = TRegistroDeModulo.objects.filter(nombre_completo=nombre_completo)

    # Paso 2: Filtrar programáticamente por 'nombre'
    existe = next((registro for registro in registros_filtrados_por_nombre_completo if registro.nombre == nombre_usuario), None)
    
    insertar_registro_accion(
                    empleado.nameUser(request),
                    'Modulo AD',
                    'Ver',
                    f"Se visualizó la contraseña del usuario. '{nombre_usuario}' ",
                    get_client_ip(request),
                    request.META.get('HTTP_USER_AGENT'),
                    'N/A'
                    )       
    
    #existe = TRegistroDeModulo.objects.filter(nombre_completo=nombre_completo).first()
        
    
    if existe:
        # Crear un diccionario con la información necesaria
        print()
        imprimir("Registro encontrado : ")
        imprimir(f'Nombre Completo: {existe.nombre_completo}, Nombre de Usuario: {existe.nombre}')
        print()
        data = {
            'nombre_completo': existe.nombre_completo,
            'modulo': existe.descripcion,
            'id': existe.id,
            'usuario' : existe.nombre
            # Añade más campos según sea necesario
        }
        return JsonResponse({'existe': data})
    else:
        imprimir("No se encontraron registros que coincidan con ambos criterios.")
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)



@login_required  
@require_http_methods(["POST"])  # vista para actualizar las contraseña del usuario 
def update_usuario (request):
    estatusModulo =" "
    estatusIDIAI =" "
    estatusAD =" "
    statusIcon= 'info'
    titulo = 'Usuario  Actualizado  '
     # Extraer el cuerpo de la solicitud y convertirlo de JSON a un diccionario de Python
    datos = json.loads(request.body)
    nombre_usuario = datos.get('nombre_usuario')
    keyPass= datos.get('keypass')
    nombre_completo = datos.get('nombre_completo')
    direccion = datos.get('direccion')
    
   # imprimir("Actualizar : Datos que recibe del POST :")
    imprimir(f'{direccion} Nombre de Usuario:{nombre_usuario} : Nombre Completo:{nombre_completo} : Contraseña : {keyPass}')
    
    # Paso 1: Filtrar por 'nombre_completo'
    registros_filtrados_por_nombre_completo = TRegistroDeModulo.objects.filter(nombre_completo=nombre_completo)

    # Paso 2: Filtrar programáticamente por 'nombre'
    existe = next((registro for registro in registros_filtrados_por_nombre_completo if registro.nombre == nombre_usuario), None)
    
          
    
    #existe = TRegistroDeModulo.objects.filter(nombre_completo=nombre_completo).first()
        
    
    if existe:
        print()
        #imprimir("Actualizar Registro encontrado : ")
        #imprimir(f'Nombre Completo: {existe.nombre_completo}, Nombre de Usuario: {existe.nombre}: Contraseña : {existe.descripcion}')
        print()
        
        #Inicio ---- codigo para cambiar la contraseña en el repositorio del modulo : 
        try:
            existe.descripcion=keyPass
            existe.save()
            #imprimir("Se Actualizo la Contraseña en el Modulo : ")
            #imprimir(f'Nombre Completo: {existe.nombre_completo}, Nombre de Usuario: {existe.nombre}: Contraseña : {existe.descripcion}')
            estatusModulo ="Modulo : OK "
            insertar_registro_accion(
                    empleado.nameUser(request),
                    'Modulo AD',
                    'Crear',
                    f"Se Actualizó la contraseña del usuario. '{nombre_usuario}' en el Modulo ",
                    get_client_ip(request),
                    request.META.get('HTTP_USER_AGENT'),
                    'N/A'
                    ) 
        except Exception as e : 
             estatusModulo =f"Modulo : Error {e}"
             imprimir(f"Error al guardar el registro en repositorios de los modulos : {e}")
             statusIcon= 'warning'
             titulo = 'Usuario  Actualizado  excepto en el Modulo '
         #FIN ---- codigo para cambiar la contraseña en el repositorio del modulo : 
        
        
         #Inicio ---- codigo para cambiar la contraseña en el repositorio del IDIAI : 
        try:
            user = User.objects.get(username=nombre_usuario)
            user.set_password(keyPass)  # Asegúrate de que la contraseña esté en texto plano aquí
            user.save()
            #imprimir("Se Actualizo la Contraseña en IDIAI: ")
            #imprimir(f'Nombre Completo: {user.get_username()}, Nombre de Usuario: {user.get_username()}: Contraseña : {keyPass}')
            estatusIDIAI  ="IDIAI V2 : OK "
            insertar_registro_accion(
                    empleado.nameUser(request),
                    'Modulo AD',
                    'Crear',
                    f"Se Actualizó la contraseña del usuario. '{nombre_usuario}' en el IDIAI V2 ",
                    get_client_ip(request),
                    request.META.get('HTTP_USER_AGENT'),
                    'N/A'
                    )
        except Exception as e : 
             estatusIDIAI =f"IDIAI V2  : Error {e}"
             imprimir(f"Error al guardar el registro en repositorios de IDIAI : {e}")
             statusIcon='warning'
             titulo = 'Usuario  Actualizado  excepto en IDIAI '
         #FIN ---- codigo para cambiar la contraseña en el repositorio del IDIAI : 
         
         
         
         #Inicio ---- codigo para cambiar la contraseña en Active Directory  : 
        try:
            # Preparar la contraseña en formato adecuado para AD
            imprimir(mover_usuario_ou(nombre_usuario, unidadOrganizativa[asignar_Departamento(direccion)],request)) 
            _password = f'"{keyPass}"'.encode('utf-16-le')
            user_dn =f'CN={nombre_usuario},{unidadOrganizativa[asignar_Departamento(direccion)]},{domino}'
            # Establecer conexión con Active Directory
            with connect_to_ad() as conn:
                conn.modify(user_dn, {'unicodePwd': [(MODIFY_REPLACE, [_password])],
                                      'userPassword': [(MODIFY_REPLACE, [_password])],
                                      'department': [(MODIFY_REPLACE, [direccion])],
                                      }) 
                if conn.result['result'] == 0:   
                   imprimir("Se Actualizo la Contraseña en Active Directory: ")
                   imprimir(f'Nombre Completo: { nombre_completo}, Nombre de Usuario: {nombre_usuario}: Contraseña : {keyPass}')
                   estatusAD  ="Active Directory : OK "
                   insertar_registro_accion(
                    empleado.nameUser(request),
                    'Modulo AD',
                    'Crear',
                    f"Se Actualizó la contraseña del usuario. '{nombre_usuario}' en el Active Directory ",
                    get_client_ip(request),
                    request.META.get('HTTP_USER_AGENT'),
                    'N/A'
                    )
                   
                   
                else:
                   titulo = 'Usuario  Actualizado  excepto en Active Directory '
                   statusIcon='warning'
                   estatusAD = f"Active Directory Error {conn.result['result']} :  {obtener_mensaje_error_ad(conn.result['result'])}"
                   imprimir(estatusAD) 
            
           
        except Exception as e : 
             titulo = 'Usuario  Actualizado  excepto en Active Directory '
             estatusAD +=f" Error {e}"
             imprimir(f"Error al guardar el registro en Active Directory : {e}")
             statusIcon='warning'
             #ten en cuenta que cambiar contraseñas en Active Directory puede requerir permisos específicos 
             # y configuraciones adicionales en el servidor de Active Directory. Asegúrate de que el usuario 
             # que ejecuta este código tenga los permisos adecuados para cambiar contraseñas en Active Directory. 
             # Además, ten precaución al manipular contraseñas en texto plano y asegúrate de que se tomen las 
             # medidas adecuadas para proteger la seguridad de las contraseñas. aquí estuvo goku XD
         #FIN ---- codigo para cambiar la contraseña en  Active Directory : 
        
        
            
        
        data = {
            'nombre_completo': existe.nombre_completo,
            'modulo': existe.descripcion,
            'id': existe.id,
            'usuario' : existe.nombre,
            'statusModulo':estatusModulo,
            'statusIDIAI' : estatusIDIAI,
            'statusAD' :estatusAD,
            'statusicon' : statusIcon,
            'titulo':titulo
            # Añade más campos según sea necesario
        }
        return JsonResponse({'existe': data})
    else:
        imprimir("No se encontraron registros que coincidan con ambos criterios.")
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)



def mover_usuario_ou(nombre_usuario, nueva_ou,request):
    mensaje = None
    try:
        with connect_to_ad() as conn:
            # Buscar el Distinguished Name (DN) actual del usuario
            search_filter = f'(sAMAccountName={nombre_usuario})'
            conn.search(search_base=domino, search_filter=search_filter, attributes=['distinguishedName'])

            if conn.entries:
                dn_actual = conn.entries[0].distinguishedName.value
                #imprimir(f"DN actual: {dn_actual}")

                # Construir el nuevo DN
                nuevo_rdn = f"CN={nombre_usuario}"
                if (nueva_ou =='0'):
                    nueva_ou_completa = f"{domino}"
                else:    
                    nueva_ou_completa = f"{nueva_ou},{domino}"
                
                imprimir(f"Nuevo DN: {nuevo_rdn}, en OU: {nueva_ou_completa}")

                # Mover el usuario a la nueva OU
                conn.modify_dn(dn_actual, nuevo_rdn, new_superior=nueva_ou_completa)
                
                if conn.result['result'] == 0:
                    mensaje = 'Usuario movido correctamente.'
                    insertar_registro_accion(
                    empleado.nameUser(request),
                    'Modulo AD',
                    'Mover',
                    f"El usuario  '{nombre_usuario}' ha sido trasladado  a la nueva ubicación : {extraer_unidad_organizativa(nueva_ou_completa)[0]}",
                    get_client_ip(request),
                    request.META.get('HTTP_USER_AGENT'),
                    'N/A'
                    )
                else:
                    mensaje = f"Error al mover usuario {conn.result['result']} :  {obtener_mensaje_error_ad(conn.result['result'])}"
            else:
                mensaje = "Usuario no encontrado en AD."
    except Exception as e:
        mensaje = f"Error al conectar con AD o al realizar la operación: {e}"

    return mensaje







def buscar_usuario_por_dn(dn_usuario):
    atributos_buscados = ['cn', 'department']
    resultado = {}

    try:
        with connect_to_ad() as conn:
            # Realizar la búsqueda utilizando el DN del usuario
            conn.search(search_base=dn_usuario, search_filter='(objectClass=person)', attributes=atributos_buscados, search_scope='BASE')
            
            if conn.entries:
                # Extraer los atributos buscados
                resultado['cn'] = conn.entries[0]['cn'].value if 'cn' in conn.entries[0] else None
                resultado['department'] = conn.entries[0]['department'].value if 'department' in conn.entries[0] else None
            else:
                resultado['error'] = 'Usuario no encontrado'
    except Exception as e:
        resultado['error'] = f"Error de conexión con AD: {e}"

    return resultado

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

def imprimir(mensaje): #funcion para imprimir en la consola  en modo desarrollador 
    if settings.DEBUG:
        print(mensaje)


def obtener_mensaje_error_ad(result_code):
  
  
  
  
    mensajes = {
        0: "La operación se realizó correctamente.",
        1: "Error interno del servidor.",
        2: "El cliente ha enviado una solicitud incorrecta al servidor.",
        32: "No se ha encontrado el objeto o usuario especificado en Active Directory.",
        49: "Las credenciales proporcionadas no son válidas.",
        50: "La contraseña proporcionada no cumple con los requisitos de complejidad.",
        52: "Problema de autenticación.",
        53: "La contraseña proporcionada no cumple con los requisitos de complejidad o no se ha encontrado el objeto especificado  ",
        68: "No se pudo encontrar la entrada especificada en Active Directory.",
        701: "Se ha excedido el límite de búsquedas en el servidor.",
        773: "El usuario debe cambiar la contraseña antes de iniciar sesión.",
        775: "El usuario ha intentado iniciar sesión demasiadas veces con una contraseña incorrecta.",
        8381: "El servicio de directorio no está disponible.",
        8641: "El servidor no es funcional."
        
        # Añade más códigos de error y mensajes correspondientes según necesites
    }
    
    
    return mensajes.get(result_code, "Ocurrió un error desconocido.")


def UsuarioActivoAD(dn_usuario):
    """
    Verifica si un usuario de Active Directory, especificado por su DN, está activo.

    Args:
        dn_usuario (str): El Distinguished Name (DN) del usuario a verificar.

    Returns:
        bool: True si el usuario está activo, False si está deshabilitado o no se encontró.
    """
    try:
        # Establecer conexión con Active Directory
        with connect_to_ad() as conn:
            # Realizar búsqueda por DN para obtener userAccountControl
            conn.search(search_base=dn_usuario, search_filter='(objectClass=user)', attributes=['userAccountControl'])

            if conn.entries:
                # Obtener el valor de userAccountControl
                user_account_control = conn.entries[0]['userAccountControl'].value
                # Verificar si el usuario está deshabilitado
                return not isAccountDisabled(user_account_control)
            else:
                imprimir(f"No se encontró el usuario con DN: {dn_usuario}")
                return False
    except Exception as e:
        imprimir(f"Error al verificar el estado del usuario: {e}")
        return False

def isAccountDisabled(useraccountcontrol_value):
    """
    Determina si el usuario está deshabilitado basado en userAccountControl.

    Args:
        useraccountcontrol_value (int): El valor de userAccountControl de un usuario.

    Returns:
        bool: True si el usuario está deshabilitado, False en caso contrario.
    """
    # Bit que indica si la cuenta está deshabilitada
    ACCOUNTDISABLE = 0x0002
    return (useraccountcontrol_value & ACCOUNTDISABLE) != 0



def obtenerUnidadesOrganizativas():
    """
    Busca y devuelve una lista de las Unidades Organizativas en el dominio especificado.

    Returns:
        list: Una lista de cadenas con los nombres de las Unidades Organizativas.
    """
    unidadesOrganizativas = []

    try:
        # Establecer conexión con Active Directory
        with connect_to_ad() as conn:
            # Especifica el dominio a buscar. Ajusta este valor según sea necesario.
            search_base = domino
            # Filtro para buscar objetos de tipo Unidad Organizativa (OU)
            search_filter = "(objectClass=organizationalUnit)"
            # Realizar la búsqueda
            conn.search(search_base=search_base, search_filter=search_filter, attributes=['name'])

            # Iterar sobre los resultados y añadir los nombres de las OUs a la lista
            for entry in conn.entries:
               unidadesOrganizativas.append('OU='+str(entry.name))

    except Exception as e:
        imprimir(f"Error al obtener las Unidades Organizativas: {e}")

    return unidadesOrganizativas




def notificacionCorreo(request,Asunto,titulo,contenido):
   
    current_year = datetime.now().year
    context = {
            'year': current_year,
            'titulo' : "IDIAI-Modulo de Active Directory",
            'Subtitulo' : titulo,
            'contenido' :contenido,
            'Usuario'   : empleado.nameUser(request)
            }
            # Renderizar el contenido HTML
    html_content = render_to_string('NotificacionCorreo.html', context)
    text_content = strip_tags(html_content)  # Esto crea una versión en texto plano del HTML

        # Crear el correo y añadir tanto el contenido en texto plano como el HTML
    email = EmailMultiAlternatives(
            Asunto,  # Asunto
            text_content,  # Contenido en texto plano
            'sistemas.iai@grupo-iai.com.mx',  # Email del remitente
            ['manuel.zarate@grupo-iai.com.mx']  # Lista de destinatarios
        )
    email.attach_alternative(html_content, "text/html")
    try:
        time.sleep(1) #para evitar que envie un moton de solicitudes 
        email.send()
        imprimir("Correo enviado correctamente.")
    except Exception as e:
        imprimir(f"Error al enviar correo: {e}")
        
   # imprimir("se envio la notificacion por correo de la creacion del correo ")
   

def usuarioexisteIDIAI(nombre_de_usuario):
    return User.objects.filter(username=nombre_de_usuario).exists()























































































