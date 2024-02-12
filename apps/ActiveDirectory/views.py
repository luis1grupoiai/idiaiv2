from django.shortcuts import render , redirect, get_object_or_404
from django.conf import settings
from ldap3 import Server, Connection, ALL_ATTRIBUTES , MODIFY_REPLACE , ALL , NTLM
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from apps.AsignarUsuario.models import VallEmpleado, TRegistroAccionesModulo 
from django.http import JsonResponse
from django.utils import timezone
from .models import TActiveDirectoryIp
import re
import time

def imprimir(mensaje):
    if settings.DEBUG:
        print(mensaje)
        
        
ip_sin_base_dato={
                    'id':'0', 
                    'server':'sin_servidor_XD' , 
                    'ip':'0.0.0.0' #esta ip debe ser cambiado en caso que no funcione la base de datos
                    
                 }#'192.192.194.10' 

def asignar_ip():
    
    if settings.DEBUG:
        ip=TActiveDirectoryIp.objects.filter(server='ADVirtual').first() #servidor de AD para el desarrollo 
    else:
        ip=TActiveDirectoryIp.objects.filter(server='ADProduccion').first() # servidor de AD  para produccion 

    return ip if ip else ip_sin_base_dato  

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

#https://www.youtube.com/watch?v=dFJvNYdKGrA&list=PLgrNDDl9MxYmUmf19zPiljdg8FKIRmP78

# Create your views here.
domino=asignar_dominio()['dominio']
dominoRaiz=asignar_dominio()['dominioRaiz']
unidadOrganizativa = ('OU=Bajas','OU=Administracion','OU=Ingeniería','OU=DCASS','OU=Proyectos Especiales') #esta variable esta relacionada con las funciones de   mover_usuario_ou y asignar_Departamento



@login_required
def ipconfig(request):
    ip=None
   
    if request.method == 'POST':
        action = request.POST.get('action')
        nueva_ip = request.POST['ip']
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
                nameUser(request),
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
            if nueva_ip and re.match(ip_regex, nueva_ip):
                registro.ip = nueva_ip  # Actualiza el campo 'ip' del registro
                time.sleep(5)
                registro.save()  # Guarda los cambios en la base de datos
                time.sleep(10)
                messages.success(request, "Registro actualizado exitosamente.")
                return redirect('ipconfig')
            else:
                # Maneja el caso en que 'nueva_ip' esté vacía
                time.sleep(5)
                messages.error(request, "La nueva IP no puede estar vacía y debe tener un formato válido (0.0.0.0).")
                return redirect('ipconfig')
        
  
    
    ip=asignar_ip()
    
    context = {
        'active_page': 'ipconfig',
        'nombre_usuario':nameUser(request),
        'ip' : ip
    }
    return render(request,'ipconfig.html',context)

@login_required  
def bitacora(request):
    mensaje=None
    #registros= TRegistroAccionesModulo.objects.all()
    registros = TRegistroAccionesModulo.objects.filter(Modulo='Modulo AD').order_by('-FechaHora')[:1000] # solo muestra los ultimos  mil registros 
    context = {
                    'active_page': 'bitacora',
                    'nombre_usuario': nameUser(request),
                    'mensaje': mensaje,
                    'registros':registros
                    }
        
    
    
    return render(request, 'bitacora.html',context)


@login_required  
def consultarUsuariosIDIAI(request):
    mensaje = None
    opc = 0
    
    
    # Obtiene los usuarios de la base de datos
    usuarios = VallEmpleado.objects.exclude(username__isnull=True).exclude(username='').exclude(is_active=False)
    UsuaruisDown = VallEmpleado.objects.exclude(username__isnull=True).exclude(username='').exclude(is_active=True)
   
    
    
    
    # Verifica la existencia en AD para cada conjunto de usuarios y agrega la información al contexto
    for conjunto_usuarios in [usuarios,UsuaruisDown]:
        for usuario in conjunto_usuarios:
            # Suponiendo que 'username' es el campo relevante para verificar en AD
           # usuario.existe_en_ad = existeUsuario(usuario.username)
            usuario.existe_en_ad = True
    
    
    usuariosAdmin =usuarios.filter(nombre_direccion="Administración")
    usuariosIng = usuarios.filter(nombre_direccion="Ingeniería")
    usuariosDCASS =usuarios.filter(nombre_direccion="Calidad, Ambiental, Seguridad y Salud")
    UsuariosPS =usuarios.filter(nombre_direccion="Proyectos Especiales")

    
     
    


    if request.method == 'POST':
        dominio_Principal ='@'+'.'.join(part.replace('DC=', '') for part in domino.split(',') if part.startswith('DC='))
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
        imprimir(password)
        # Preparar la contraseña en formato adecuado para AD
        quoted_password = f'"{password}"'.encode('utf-16-le')
        imprimir(quoted_password )
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
                   
                    # ... otros atributos
                })
                # Verificar el resultado de la creación del usuario
                if conn.result['result'] == 0:  # éxito
                    messages.success(request, 'Usuario creado correctamente.')
                    mensaje = {'titulo': 'Éxito', 'texto': 'Usuario creado correctamente', 'tipo': 'success'}
                    #codigo para guardar en la bitacora -------
                    insertar_registro_accion(
                    nameUser(request),
                    'Modulo AD',
                    'Crear',
                    f"El usuario '{nombre_usuario}' fue creado en AD",
                    get_client_ip(request),
                    request.META.get('HTTP_USER_AGENT'),
                    'N/A'
                    )
                    
                    #return redirect('usuariosID')
                    
                    
                else:
                    messages.error(request, f"Error al crear usuario: {conn.result['description']}")
                    mensaje = {'titulo': 'Error', 'texto': f"Error al crear usuario {conn.result['description']}", 'tipo': 'error'}
                    imprimir(mensaje)
                    #return redirect('usuariosID')
        except Exception as e:
            messages.error(request, f"Error al conectar con AD: {str(e)}")
            mensaje = {'titulo': 'Error', 'texto': f'Excepción: {str(e)}', 'tipo': 'error'}
            imprimir(mensaje)
            return redirect('usuariosID')
    
    context = {
                    'active_page': 'usuariosID',
                    'nombre_usuario': nameUser(request),
                    'users': usuarios,
                    'usersDown' : UsuaruisDown,
                    'usersAdmin': usuariosAdmin,
                    'usersIng': usuariosIng,
                    'usersDCASS':usuariosDCASS,
                    'usersPS':UsuariosPS,
                    'mensaje': mensaje,
                    }
        
    
    
    return render(request, 'UsuariosIDIAI.html',context)














@login_required  
def consultar_usuarios(request):
    # Establece la conexión con el servidor de Active Directory
    #imprimir(dominoRaiz)
    #imprimir(domino)
    usuarios = []
    usuariosAdmin =[]
    usuariosIng = []
    usuariosDCASS =[]
    UsuariosPS =[]
    UsuaruisDown=[]
    try:
        #server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
        with connect_to_ad() as connection:
            search_base = domino #dominoRaiz
            #search_filter = '(objectClass=user)'
            search_filter = '(&(objectClass=user)(!(OU=Administracion)))'
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
                    'oficina': entry.physicalDeliveryOfficeName.value if 'physicalDeliveryOfficeName' in entry else None,
                    'descripcion': entry.description.value if 'description' in entry else None,
                    'departamento': entry.department.value if 'department' in entry else None,  # Nuevo atributo
                    'puesto': entry.title.value if 'title' in entry else None,  # Nuevo atributo
                    'userAccountControl': entry.userAccountControl.value if 'userAccountControl' in entry else None,
                    'esta_deshabilitado': is_account_disabled(useraccountcontrol_str),
                    'DistinguishedName' : entry.distinguishedName.value if 'DistinguishedName' in entry else None,
        
                }
                #imprimir(entry.cn.value)
                #imprimir(entry.distinguishedName.value if 'distinguishedName' in entry else None)
                #imprimir(entry.userPrincipalName.value)
                #imprimir(entry.distinguishedName.value)
                #imprimir(extraer_unidad_organizativa(entry.distinguishedName.value))
              
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
        'nombre_usuario': nameUser(request)# Variable adicional
        # Puedes agregar más variables aquí si lo necesitas
    }
    # Renderiza la lista de usuarios en una plantilla HTML
    return render(request, 'Usuarios.html', context)



@login_required  
def agregar_usuario(request): # esta funcion o vista la deje por que tal vez se utilice en el futuro , solo revisien bien las variables porque se han modificado el domino.....
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
                    #'unicodePwd':quoted_password,
                    #'userAccountControl':'546', # Habilita la cuenta
                   
                    # ... otros atributos
                })
                # Verificar el resultado de la creación del usuario
                if conn.result['result'] == 0:  # éxito
                    messages.success(request, 'Usuario creado correctamente.')
                    
                else:
                    messages.error(request, f"Error al crear usuario: {conn.result['description']}")
        except Exception as e:
            messages.error(request, f"Error al conectar con AD: {str(e)}")
            
            return redirect('usuarios')
  # Crear el diccionario de contexto con todas las variables necesarias
    context = {
        'active_page': 'agregar_usuario',
        'nombre_usuario': nameUser(request)# Variable adicional para el boton del menu 
        # Puedes agregar más variables aquí si lo necesitas
    }          
    
    return render(request, 'AgregarUsuario.html',context)

@login_required  
def editar_usuario(request):
    #imprimir("Vista de editar Usuario ")
    if request.method == 'POST':
         # Captura los datos enviados desde el formulario
        nombre_usuario = request.POST.get('nombre_usuario')
        nombre_pila = request.POST.get('nombre_pila')
        apellido = request.POST.get('apellido')
        nombre_completo = request.POST.get('nombre_completo')
        email = request.POST.get('email')
        departamento = request.POST.get('departamento')
        puesto = request.POST.get('puesto')
        nombre_inicio_sesion = request.POST.get('nombre_inicio_sesion')
        user_dn = request.POST.get('distinguished_name')
        # ... otros campos ....
        #imprimir(nombre_usuario)
        #imprimir(user_dn)
        # Conectar a Active Directory
        insertar_registro_accion(
        nameUser(request),
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
                    # ... otros atributos ...
                })

                # Verificar resultado de la modificación
                if conn.result['result'] == 0:  # éxito
                    messages.success(request, 'Usuario editado correctamente.')
                    imprimir('Usuario editado correctamente.')
                else:
                    messages.error(request, f"Error al editar usuario: {conn.result['description']}")
                    imprimir( f"Error al editar usuario: {conn.result['description']}")
        except Exception as e:
            messages.error(request, f"Error al conectar con AD: {str(e)}")
            imprimir(f"Error al conectar con AD: {str(e)}")
    # Redireccionar de vuelta a la lista de usuarios
    
    imprimir(mover_usuario_ou(nombre_inicio_sesion, unidadOrganizativa[asignar_Departamento(departamento)],request))
    return redirect('usuarios')

 
@login_required
def home(request):
    # Aquí la lógica para mostrar la página de inicio
    return render(request, 'home.html')
@login_required  
def salir (request):
    logout(request)
    return redirect ('home')


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
            #imprimir(user_dn)
            # Establecer userAccountControl a 512 para activar la cuenta
            conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [512])]}) # debe activarse con el 512 pero eso lo vamos a dejar al ultimo ajajajajaj
            if conn.result['result'] == 0:
                messages.success(request, 'Usuario activado correctamente.')
                imprimir('Usuario activado correctamente.')
                mover = buscar_usuario_por_dn(nombre_usuario)
                imprimir(mover_usuario_ou(mover['cn'], unidadOrganizativa[asignar_Departamento(mover['department'])],request))
                insertar_registro_accion(
                nameUser(request),
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
                nameUser(request),
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


def nameUser(request):
    if request.user.is_authenticated:
        nombreUsuario = request.user.first_name+" "+request.user.last_name 
    
    return  nombreUsuario


def connect_to_ad():
    servidorAD = obtener_servidor_ad()
    imprimir(servidorAD)
    server = Server(servidorAD, port=settings.AD_PORT,use_ssl=True, get_info=ALL_ATTRIBUTES)
    
    return Connection(server, user=settings.AD_USER, password=settings.AD_PASSWORD, auto_bind=True)

def verificar_usuario(request, nombre_usuario):
    existe = existeUsuario(nombre_usuario)
    return JsonResponse({'existe': existe}) 


def mover_usuario_ou(nombre_usuario, nueva_ou,request):
    mensaje = None
    try:
        with connect_to_ad() as conn:
            # Buscar el Distinguished Name (DN) actual del usuario
            search_filter = f'(sAMAccountName={nombre_usuario})'
            conn.search(search_base=dominoRaiz, search_filter=search_filter, attributes=['distinguishedName'])

            if conn.entries:
                dn_actual = conn.entries[0].distinguishedName.value
                #imprimir(f"DN actual: {dn_actual}")

                # Construir el nuevo DN
                nuevo_rdn = f"CN={nombre_usuario}"
                nueva_ou_completa = f"{nueva_ou},{domino}"
                #imprimir(f"Nuevo DN: {nuevo_rdn}, en OU: {nueva_ou_completa}")

                # Mover el usuario a la nueva OU
                conn.modify_dn(dn_actual, nuevo_rdn, new_superior=nueva_ou_completa)
                
                if conn.result['result'] == 0:
                    mensaje = 'Usuario movido correctamente.'
                    insertar_registro_accion(
                    nameUser(request),
                    'Modulo AD',
                    'Mover',
                    f"El usuario  '{nombre_usuario}' ha sido trasladado  a la nueva ubicación : {extraer_unidad_organizativa(nueva_ou_completa)[0]}",
                    get_client_ip(request),
                    request.META.get('HTTP_USER_AGENT'),
                    'N/A'
                    )
                else:
                    mensaje = f"Error al mover usuario: {conn.result['description']}"
            else:
                mensaje = "Usuario no encontrado en AD."
    except Exception as e:
        mensaje = f"Error al conectar con AD o al realizar la operación: {e}"

    return mensaje


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
        opc = 0
    return opc






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








































































































"""
librerias que hacen funcionar el proyecto ;) esto es un regalo de mi para el futuro XD 02/02/2024
absl-py                       2.0.0
annotated-types               0.6.0
asgiref                       3.7.2
attrs                         23.1.0
bcrypt                        4.1.1
certifi                       2023.11.17
cffi                          1.16.0
charset-normalizer            3.3.2
click                         8.1.7
cmake                         3.27.7
colorama                      0.4.6
contourpy                     1.2.0
cryptography                  41.0.7
cycler                        0.12.1
Django                        4.2.7
django-components             0.29
django-jazzmin                2.6.0
django-mssql-backend          2.8.1
django-querycount             0.8.3
django-sslserver              0.22
django-unfold                 0.18.0
djangorestframework           3.14.0
djangorestframework-simplejwt 5.3.1
dlib                          19.24.2
dotty-dict                    1.3.1
drf-yasg                      1.21.7
face-recognition              1.3.0
face_recognition_models       0.3.0
flatbuffers                   23.5.26
fonttools                     4.46.0
gitdb                         4.0.11
GitPython                     3.1.40
gunicorn                      21.2.0
idna                          3.6
importlib-resources           6.1.1
inflection                    0.5.1
Jinja2                        3.1.2
kiwisolver                    1.4.5
ldap3                         2.9.1
markdown-it-py                3.0.0
MarkupSafe                    2.1.3
matplotlib                    3.8.2
mdurl                         0.1.2
mediapipe                     0.10.8
mssql-django                  1.3
numpy                         1.26.2
opencv-contrib-python         4.8.1.78
opencv-python                 4.8.1.78
packaging                     23.2
passlib                       1.7.4
Pillow                        10.1.0
pip                           23.3.2
protobuf                      3.20.3
psycopg2                      2.9.9
pyasn1                        0.5.1
pycparser                     2.21
pycryptodome                  3.20.0
pydantic                      2.5.3
pydantic_core                 2.14.6
Pygments                      2.17.2
PyJWT                         2.8.0
pyodbc                        5.0.1
pyparsing                     3.1.1
python-dateutil               2.8.2
python-dotenv                 1.0.0
python-gitlab                 4.3.0
python-semantic-release       8.7.0
pytz                          2023.3.post1
PyYAML                        6.0.1
requests                      2.31.0
requests-toolbelt             1.0.0
rich                          13.7.0
setuptools                    65.5.0
shellingham                   1.5.4
six                           1.16.0
smmap                         5.0.1
sounddevice                   0.4.6
sqlparse                      0.4.4
tomlkit                       0.12.3
typing_extensions             4.9.0
tzdata                        2023.3
uritemplate                   4.1.1
urllib3                       2.1.0
wfastcgi                      3.0.0
whitenoise                    6.6.0
"""
