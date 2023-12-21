from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

@login_required
def solicitud(request):
    # Aquí la lógica para mostrar la página de inicio
    context = {
        'active_page': 'solicitud'
    }
    return render(request, 'personal.html',context)