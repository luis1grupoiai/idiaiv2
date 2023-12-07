from django.shortcuts import render , redirect
from django.conf import settings
from ldap3 import Server, Connection, ALL_ATTRIBUTES , MODIFY_REPLACE
from django.contrib import messages
from django.conf import settings
import random

# Create your views here.


def consultar_usuarios(request):
    # Establece la conexión con el servidor de Active Directory
    usuarios = []
    try:
        server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
        with Connection(server, user=settings.AD_USER, password=settings.AD_PASSWORD, auto_bind=True) as connection:
            search_base = 'DC=iai,DC=com,DC=mx'
            search_filter = '(objectClass=user)'
            attributes = ['cn', 'sn', 'givenName', 'userPrincipalName', 'mail', 'displayName', 'sAMAccountName', 'distinguishedName', 'physicalDeliveryOfficeName', 'description','department','title','userAccountControl']
            
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
                    'estatus' :random.randint(0, 1),
                    'userAccountControl': entry.userAccountControl.value if 'userAccountControl' in entry else None,
                    'esta_deshabilitado': is_account_disabled(useraccountcontrol_str),
        
                }
                #print(entry.cn.value)
               # print(entry.distinguishedName.value if 'distinguishedName' in entry else None)
                usuarios.append(usuario)
    except Exception  as e:
        # Manejar la excepción, por ejemplo, registrando el error
        print(f"Error al conectar o buscar en Active Directory: {str(e)}")
    
    # Crear el diccionario de contexto con todas las variables necesarias
    context = {
        'users': usuarios,  # Lista de usuarios
        'active_page': 'usuarios'  # Variable adicional
        # Puedes agregar más variables aquí si lo necesitas
    }
    # Renderiza la lista de usuarios en una plantilla HTML
    return render(request, 'Usuarios.html', context)


def agregar_usuario(request):
    if request.method == 'POST':
        dominio_Principal = '@iai.com.mx'
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
            server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
            with Connection(server, user=settings.AD_USER, password=settings.AD_PASSWORD, auto_bind=True) as conn:
                
                #user_dn = f"CN={nombre_usuario},CN=Users,DC=iai,DC=com,DC=mx"
                user_dn = f"CN={nombre_usuario},OU=iaiUsuario,OU=RedGrupoIAI,DC=iai,DC=com,DC=mx"
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
        'active_page': 'agregar_usuario'  # Variable adicional para el boton del menu 
        # Puedes agregar más variables aquí si lo necesitas
    }          
    
    return render(request, 'AgregarUsuario.html',context)


def editar_usuario(request):
    print("Vista editar Usuario ")
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
        # ... otros campos ....
        print(nombre_usuario)
        print(nombre_pila)
        # Conectar a Active Directory
        try:
            server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
            with Connection(server, user=settings.AD_USER, password=settings.AD_PASSWORD, auto_bind=True) as conn:
                user_dn = f"CN={nombre_usuario},OU=iaiUsuario,OU=RedGrupoIAI,DC=iai,DC=com,DC=mx"
                
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
                    print(request, 'Usuario editado correctamente.')
                else:
                    messages.error(request, f"Error al editar usuario: {conn.result['description']}")
                    print(request, f"Error al editar usuario: {conn.result['description']}")
        except Exception as e:
            messages.error(request, f"Error al conectar con AD: {str(e)}")
            print(request, f"Error al conectar con AD: {str(e)}")
    # Redireccionar de vuelta a la lista de usuarios
    return redirect('usuarios')

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
    
def activar_usuario(request, nombre_usuario):
    print("entro a activar el usuario :"+str(nombre_usuario))
    try:
        server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
        with Connection(server, user=settings.AD_USER, password=settings.AD_PASSWORD, auto_bind=True) as conn:
            user_dn = f"CN={nombre_usuario},OU=iaiUsuario,OU=RedGrupoIAI,DC=iai,DC=com,DC=mx"
            # Establecer userAccountControl a 512 para activar la cuenta
            conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [544])]})
            if conn.result['result'] == 0:
                messages.success(request, 'Usuario activado correctamente.')
                print(request, 'Usuario activado correctamente.')
                return redirect('usuarios')
            else:
                messages.error(request, f"Error al activar usuario: {conn.result['description']}")
                print(request, f"Error al activar usuario: {conn.result['description']}")
    except Exception as e:
        messages.error(request, f"Error al conectar con AD: {str(e)}")
        print(request, f"Error al conectar con AD: {str(e)}")

    
    
    

def desactivar_usuario(request, nombre_usuario):
    print("entro a activar el usuario :"+str(nombre_usuario))
    try:
        server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
        with Connection(server, user=settings.AD_USER, password=settings.AD_PASSWORD, auto_bind=True) as conn:
            user_dn = f"CN={nombre_usuario},OU=iaiUsuario,OU=RedGrupoIAI,DC=iai,DC=com,DC=mx"
            # Establecer userAccountControl a 66050 para desactivar la cuenta
            conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [66050])]})
            if conn.result['result'] == 0:
                messages.success(request, 'Usuario desactivado correctamente.')
                print(request, 'Usuario desactivado correctamente.')
                return redirect('usuarios')
            else:
                messages.error(request, f"Error al desactivar usuario: {conn.result['description']}")
                print(request, f"Error al desactivar usuario: {conn.result['description']}")
    except Exception as e:
        messages.error(request, f"Error al conectar con AD: {str(e)}")
        print(request, f"Error al conectar con AD: {str(e)}")

    