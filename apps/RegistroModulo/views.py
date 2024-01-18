from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import TRegistroDeModulo
from .forms import ModuloForm
from cryptography.fernet import Fernet
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin

class NombreUsuarioMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.first_name and user.last_name:
            context['nombre_usuario'] = user.first_name + " " + user.last_name
        else:
            context['nombre_usuario'] = user.username
        return context


class ModuloListView(LoginRequiredMixin,NombreUsuarioMixin,ListView):
    model = TRegistroDeModulo
    template_name = 'modulo_list.html'
    

class ModuloCreateView(LoginRequiredMixin,NombreUsuarioMixin,CreateView):
    model = TRegistroDeModulo
    form_class = ModuloForm
    template_name = 'modulo_form.html'
    success_url = '/RegistroModulo/'

class ModuloUpdateView(LoginRequiredMixin,NombreUsuarioMixin,UpdateView):
    model = TRegistroDeModulo
    form_class = ModuloForm
    template_name = 'modulo_form.html'
    success_url = '/RegistroModulo/'

class ModuloDeleteView(LoginRequiredMixin,NombreUsuarioMixin,DeleteView):
    model = TRegistroDeModulo
    template_name = 'modulo_confirm_delete.html'
    success_url = '/RegistroModulo/'
# Create your models here.






@login_required 
def ver_detalle_registro(request, id):
    registro = get_object_or_404(TRegistroDeModulo, pk=id)
    modulo_desencriptada = registro.descripcion
    # Genera una clave segura
    #ENCRYPTION_KEY = Fernet.generate_key()

    # Puedes imprimir la clave para almacenarla y usarla posteriormente
   # print(ENCRYPTION_KEY)
    if request.user.is_authenticated:
        nombreUsuario = request.user.first_name+" "+request.user.last_name
        
        
    context = {
        'registro': registro,
        'modulo_desencriptada': modulo_desencriptada,
        'nombre_usuario': nombreUsuario
    }
    return render(request, 'detalle_registro.html', context)

    """
    
    
    la línea de código from django.views.generic import ListView, CreateView, 
    UpdateView, DeleteView es una importación de clases de vistas genéricas de Django, 
    un framework de desarrollo web en Python. Vamos a desglosar cada clase:

ListView: Esta clase se utiliza para mostrar una lista de objetos. Por ejemplo, si
tienes un modelo que representa artículos de un blog, puedes usar ListView para mostrar 
una lista de todos los artículos.

CreateView: Esta clase se usa para crear un nuevo objeto. Utiliza un formulario para 
tomar los datos del usuario y, tras la validación, los guarda en la base de datos. 
Por ejemplo, puedes usar CreateView para permitir a los usuarios crear un nuevo 
artículo de blog.

UpdateView: Similar a CreateView, pero se utiliza para actualizar un objeto existente. 
Esta vista también utiliza un formulario, pero se rellena con la información del objeto 
que se va a actualizar.

DeleteView: Esta clase se usa para eliminar un objeto. Generalmente muestra una 
confirmación antes de proceder a la eliminación del objeto de la base de datos.

Estas vistas genéricas son parte del patrón de diseño MVC (Modelo-Vista-Controlador) 
que Django implementa y ayudan a reducir la cantidad de código que necesitas escribir para realizar operaciones comunes en aplicaciones web. Cada una de estas clases está diseñada para manejar una operación específica de CRUD (Crear, Leer, Actualizar, Eliminar) y se integra estrechamente con el sistema de modelos y plantillas de Django.
    """