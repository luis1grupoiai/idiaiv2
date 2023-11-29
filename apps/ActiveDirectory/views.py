from django.shortcuts import render , redirect
from django.conf import settings
from ldap3 import Server, Connection, ALL_ATTRIBUTES
from django.contrib import messages
# Create your views here.


def consultar_usuarios(request):
    # Establece la conexión con el servidor de Active Directory
    usuarios = []
    try:
        server = Server(settings.AD_SERVER, port=settings.AD_PORT, get_info=ALL_ATTRIBUTES)
        with Connection(server, user=settings.AD_USER, password=settings.AD_PASSWORD, auto_bind=True) as connection:
            search_base = 'DC=iai,DC=com,DC=mx'
            search_filter = '(objectClass=user)'
            attributes = ['cn', 'sn', 'givenName', 'userPrincipalName', 'mail', 'displayName', 'sAMAccountName', 'distinguishedName', 'physicalDeliveryOfficeName', 'description','department','title']

            connection.search(search_base, search_filter, attributes=attributes)
            for entry in connection.entries:
                domain_name = '.'.join(part.replace('DC=', '') for part in entry.distinguishedName.value.split(',') if part.startswith('DC='))
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
        
                }
                #print(entry.cn.value)
               # print(entry.distinguishedName.value if 'distinguishedName' in entry else None)
                usuarios.append(usuario)
    except Exception  as e:
        # Manejar la excepción, por ejemplo, registrando el error
        print(f"Error al conectar o buscar en Active Directory: {str(e)}")

    # Renderiza la lista de usuarios en una plantilla HTML
    return render(request, 'Usuarios.html', {'users': usuarios})


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
            
            
    
    return render(request, 'AgregarUsuario.html')