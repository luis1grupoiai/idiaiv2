from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Vempleado
@login_required
def solicitud(request):
    # Aquí la lógica para mostrar la página de inicio
    empleados = []
    empleados=Vempleado.objects.all()
    
    print(empleados)
    context = {
        'empleados' : empleados,
        'active_page': 'solicitud'
    }
    return render(request, 'personal.html',context)