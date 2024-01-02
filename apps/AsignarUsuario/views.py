from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import VallEmpleado 
from django.db.models import Q





@login_required
def solicitud(request):
    # Aquí la lógica para mostrar la página de inicio
    
    
        
    empleados = []
    empleados = VallEmpleado.objects.exclude(username__isnull=True).exclude(username='')
    
   # print(empleados)
    context = {
        'empleados' : empleados,
        'active_page': 'solicitud',
        'nombre_usuario': nameUser(request)
    }
    return render(request, 'personal.html',context)

@login_required
def solicitudNuevos(request):
    # Aquí la lógica para mostrar la página de inicio
    empleados = []
    empleados = VallEmpleado.objects.filter(Q(username__isnull=True) )
    if request.user.is_authenticated:
        nombreUsuario = request.user.first_name+" "+request.user.last_name 
   # print(empleados)
    context = {
        'empleados' : empleados,
        'active_page': 'Nsolicitud',
        'nombre_usuario': nameUser(request)
    }
    return render(request, 'nuevoPersonal.html',context)


def nameUser(request):
    if request.user.is_authenticated:
        nombreUsuario = request.user.first_name+" "+request.user.last_name 
    
    return  nombreUsuario
