
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import VUsuarioDjango
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

def es_superusuario(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(es_superusuario)
def importar_usuarios(request):
    
    usuarios_vista = VUsuarioDjango.objects.all()  # Obtener todos los registros de la vista
    if request.method == "POST":
       count=0
       for usuario in usuarios_vista:
           count+=1
           print(count)
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
              print(usuario.username)
              user.set_password(usuario.password)  # Asegúrate de que la contraseña esté en texto plano aquí
              user.save()
              
       messages.success(request, "Usuarios importados correctamente.")
       return redirect('importarusuarios')  # Redirige según corresponda
        
    context = {
        'active_page': 'importar'
       # 'nombre_usuario':nameUser(request),
       # 'foto':photoUser(request),
       # 'Categoria': Categoria(request)
    }
    return render(request,'importar_usuarios.html',context) # Redirige a donde consideres apropiado después de la importación