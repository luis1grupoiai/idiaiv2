from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import VUsuarioDjango
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import VUsuariosModulo, TRegistroDeModulo 
from cryptography.fernet import Fernet
import os
# Asegúrate de definir tus claves aquí o importarlas desde tu configuración
ENCRYPTION_KEY_DESCRIPCION =os.environ.get('KEY_DESCRIPCION').encode()
ENCRYPTION_KEY_NOMBRE = os.environ.get('KEY_NOMBRE').encode()

def es_superusuario(user):
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(lambda user: user.is_superuser)  # Solo permitir a superusuarios
def importarmodulo(request):   #cambia el nombre a importarmodulo cuando quieran importar todos los modulos 
    if request.method == "POST":
        n = Fernet(ENCRYPTION_KEY_NOMBRE)
        f = Fernet(ENCRYPTION_KEY_DESCRIPCION)
        usuarios = VUsuariosModulo.objects.all()
        count=usuarios.count()
        for usuario in usuarios:
            count-=1
            # Cifrar el nombre y la descripción
            nombre_cifrado = n.encrypt(usuario._nombre.strip().encode()).decode()
            descripcion_cifrado = f.encrypt(usuario._descripcion.encode()).decode()

            # Intentar obtener o crear un nuevo registro en TRegistroDeModulo
            # Asegúrate de usar los campos correctos para definir la "unicidad"
            obj, created = TRegistroDeModulo.objects.get_or_create(
                _nombre=nombre_cifrado,  # Este campo determina la unicidad junto con nombre_completo NO FUNCIONA POR QUE ENCRIPTA DIFERENTE ......
                defaults={
                    'nombre_completo': usuario.nombre_completo,  # Asumiendo que quieres actualizar este campo si _nombre coincide
                    '_descripcion': descripcion_cifrado,
                }
            )

            if created:
                print(f"{count}: Nuevo registro creado: {usuario.nombre_completo}, Nombre: {usuario._nombre}")
            else:
                # Si el registro ya existe y quieres actualizar otros campos, puedes hacerlo aquí
                obj._descripcion = descripcion_cifrado  # Por ejemplo, actualizar la descripción
                obj.save()
                print(f"{count}:Registro existente actualizado: {usuario.nombre_completo}, Nombre: {usuario._nombre}")

        messages.success(request, "Usuarios importados correctamente.")
        return redirect('importarmodulos')

    # Si es GET, mostrar la página con el formulario
    return render(request, 'importar_modulos.html')





@login_required
@user_passes_test(lambda user: user.is_superuser)  # Solo permitir a superusuarios
def importarmodulo__(request):  # deja de guncionar cuando tiene mulple registro , se tiene que mejorar el codigo manuel zarate 
    if request.method == "POST":
        n = Fernet(ENCRYPTION_KEY_NOMBRE)
        f = Fernet(ENCRYPTION_KEY_DESCRIPCION)
        usuarios = VUsuariosModulo.objects.all()
        count=usuarios.count()
        for usuario in usuarios:
            count-=1
            # Cifrar el nombre y la descripción
            nombre_cifrado = n.encrypt(usuario._nombre.encode()).decode()
            descripcion_cifrado = f.encrypt(usuario._descripcion.encode()).decode()
            nombreCompleto = usuario.nombre_completo
            # Intentar obtener o crear un nuevo registro en TRegistroDeModulo
            nuevo_usuario, created = TRegistroDeModulo.objects.get_or_create(
                
                nombre_completo=nombreCompleto,
                defaults={
                    '_descripcion': descripcion_cifrado, '_nombre':nombre_cifrado,
                    
                }
            )
            
            if created:
                nuevo_usuario.save()
                print(count,"Usuario creado:", usuario.nombre_completo , usuario._nombre )    # Opcional: imprimir/loguear los nombres de los usuarios creados
            else:
                print(" ") 
                print(count,"Usuario existente:", usuario.nombre_completo , usuario._nombre) 

         
                         
                    

        messages.success(request, "Usuarios importados correctamente.")
        return redirect('importarmodulos')  # Asegúrate de que este nombre de URL exista en tus urls.py

    # Si es GET, mostrar la página con el formulario
    return render(request, 'importar_modulos.html')






@login_required
@user_passes_test(es_superusuario)
def importar_usuarios(request):
    
   
    if request.method == "POST":
       usuarios_vista = VUsuarioDjango.objects.all()  # Obtener todos los registros de la vista
       count=usuarios_vista.count()
       for usuario in usuarios_vista:
           count-=1
           user, created = User.objects.get_or_create(username=usuario.username, defaults={
                'email': usuario.email,
                'first_name': usuario.first_name,
                'last_name': usuario.last_name,
                'is_active': usuario.is_active,
                'is_superuser': usuario.is_superuser,
                'is_staff': usuario.is_staff,
                'last_login': usuario.last_login,
                'date_joined': usuario.date_joined,
            })
           if created:
              user.set_password(usuario.password)  # Asegúrate de que la contraseña esté en texto plano aquí
              user.save()
              print(count,"Usuario creado:", usuario.username)  # Opcional: imprimir/loguear los nombres de los usuarios creados
           else:
              print(count,"Usuario existente:", usuario.username)
              
       messages.success(request, "Usuarios importados correctamente.")
       return redirect('importarusuarios')  # Redirige según corresponda
        
    context = {
        'active_page': 'importar'
       # 'nombre_usuario':nameUser(request),
       # 'foto':photoUser(request),
       # 'Categoria': Categoria(request)
    }
    return render(request,'importar_usuarios.html',context) # Redirige a donde consideres apropiado después de la importación


