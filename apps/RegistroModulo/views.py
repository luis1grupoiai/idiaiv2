from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import TRegistroDeModulo 
from apps.AsignarUsuario.models import  TRegistroAccionesModulo ,VallEmpleado
from .forms import ModuloForm
from cryptography.fernet import Fernet
from django.contrib.auth.decorators import login_required , user_passes_test
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib import messages
from .mixins import SuperuserRequiredMixin , SuperuserRedirectMixin

ModuloEntrada ="12345" # la contraseña del modal ----
def es_superusuario(user):
    return user.is_authenticated and user.is_superuser

class NombreUsuarioMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.first_name and user.last_name:
            context['nombre_usuario'] = user.first_name + " " + user.last_name
        else:
            context['nombre_usuario'] = user.username
        
        context['foto'] = photoUser(self.request)
        context['Categoria'] = Categoria(self.request)
        context['active_page']='modulos'
        
        return context


class ModuloListView(LoginRequiredMixin,NombreUsuarioMixin,SuperuserRedirectMixin,ListView):
    model = TRegistroDeModulo
    template_name = 'modulo_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verificar'] = ModuloEntrada
        
        return context

class ModuloCreateView(LoginRequiredMixin,NombreUsuarioMixin,SuperuserRedirectMixin,CreateView):
    model = TRegistroDeModulo
    form_class = ModuloForm
    template_name = 'modulo_form.html'
    success_url = reverse_lazy('modulo_list')
    
    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['verificar'] = ModuloEntrada
       return context   
    
    
    def form_valid(self, form):
        
        response = super(ModuloCreateView, self).form_valid(form)
        # Obtén la información del usuario y otros detalles aquí
        nombreUsuario = self.request.user.get_full_name()  # O tu método personalizado

        # Insertar el registro de acción
        insertar_registro_accion(
            nombreUsuario,
            'Modulo',
            'Nuevo',
            f"Se creo el módulo {self.object.nombre}",
            get_client_ip(self.request),
            self.request.META.get('HTTP_USER_AGENT'),
            'N/A'
        )

        return response

class ModuloUpdateView(LoginRequiredMixin,NombreUsuarioMixin,SuperuserRequiredMixin,UpdateView):
    model = TRegistroDeModulo
    form_class = ModuloForm
    template_name = 'modulo_form.html'
    success_url = reverse_lazy('modulo_list')
    

   
    
    def get_initial(self):
        initial = super().get_initial()
        # Obtén la instancia del módulo que se va a actualizar
        modulo = self.get_object()
        # Establece los valores iniciales desencriptados para el formulario
        initial['nombre'] = modulo.nombre
        #initial['descripcion'] = modulo.descripcion
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verificar'] = ModuloEntrada
        return context    
    
    
    def form_valid(self, form):
        # Validación para el nombre
        modulo = self.get_object()
        if form.cleaned_data['nombre'] != modulo.nombre:
           messages.error(self.request, 'No puedes cambiar el nombre del módulo.')
           return self.form_invalid(form)
       
        # Validación para la descripción
        descripcion = form.cleaned_data.get('descripcion')
        if not descripcion:
            messages.error(self.request, 'La descripción no puede estar vacía.')
            return self.form_invalid(form)
         # Procesamiento normal si todas las validaciones pasan
        response = super(ModuloUpdateView, self).form_valid(form)
        # Obtén la información del usuario y otros detalles aquí
        nombreUsuario = self.request.user.get_full_name()  # O tu método personalizado

        # Insertar el registro de acción
        insertar_registro_accion(
            nombreUsuario,
            'Modulo',
            'Editar',
            f"Se actualizó el módulo {self.object.nombre}",
            get_client_ip(self.request),
            self.request.META.get('HTTP_USER_AGENT'),
            'N/A'
        )

        return response
    
    

class ModuloDeleteView(LoginRequiredMixin,NombreUsuarioMixin,SuperuserRequiredMixin,DeleteView):
    model = TRegistroDeModulo
    template_name = 'modulo_confirm_delete.html'
    success_url = reverse_lazy('modulo_list')
    
    def form_valid(self, form):
        response = super(ModuloDeleteView, self).form_valid(form)
        # Obtén la información del usuario y otros detalles aquí
        nombreUsuario = self.request.user.get_full_name()  # O tu método personalizado

        # Insertar el registro de acción
        insertar_registro_accion(
            nombreUsuario,
            'Modulo',
            'Borrar',
            f"Se borro el módulo {self.object.nombre}",
            get_client_ip(self.request),
            self.request.META.get('HTTP_USER_AGENT'),
            'N/A'
        )

        return response

@login_required  
@user_passes_test(es_superusuario) # Solo permitir a superusuarios
def bitacora(request):
    
    
    mensaje=None
    #registros= TRegistroAccionesModulo.objects.all()
    registros = TRegistroAccionesModulo.objects.filter(Modulo='Modulo').order_by('-FechaHora')[:1000] # solo muestra los ultimos  mil registros 
    if request.user.is_authenticated:
        nombreUsuario = request.user.first_name+" "+request.user.last_name
    
    """
    insertar_registro_accion(
                nombreUsuario,
                'Modulo',
                'Revisar',
                f"Se visualizo la bitácora del modulo ",
                get_client_ip(request),
                request.META.get('HTTP_USER_AGENT'),
                'N/A'
                )"""
     
    context = {
                    'active_page': 'bitacoraModulo',
                    'nombre_usuario': nombreUsuario,
                    'mensaje': mensaje,
                    'registros':registros,
                    'foto':photoUser(request),
                    'Categoria': Categoria(request)
                    }
        
  
    
    return render(request, 'bitacora2.html',context)




@login_required 
@user_passes_test(es_superusuario) # Solo permitir a superusuarios
def ver_detalle_registro(request, id):
    registro = get_object_or_404(TRegistroDeModulo, pk=id)
    modulo_desencriptada = registro.descripcion
    
    
    if request.user.is_authenticated:
        nombreUsuario = request.user.first_name+" "+request.user.last_name
        
    insertar_registro_accion(
                nombreUsuario,
                'Modulo',
                'Ver',
                f"Se visualizo la descripción del usuario '{registro}'",
                get_client_ip(request),
                request.META.get('HTTP_USER_AGENT'),
                'N/A'
                )
    # Genera una clave segura
    #ENCRYPTION_KEY = Fernet.generate_key()

    # Puedes imprimir la clave para almacenarla y usarla posteriormente
   # print(ENCRYPTION_KEY)
    
        
         
    context = {
        'registro': registro,
        'modulo_desencriptada': modulo_desencriptada,
        'nombre_usuario': nombreUsuario,
        'verificar':ModuloEntrada,
        'foto':photoUser(request),
        'Categoria': Categoria(request),
        'active_page':'modulos'
    }
    return render(request, 'detalle_registro.html', context)

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
    print(nuevo_registro)
    
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
    
    
def photoUser(request):
    # Ruta de foto predeterminada
    photo = '/static/img/logo1.png'

    # Comprobar si el usuario está autenticado
    if request.user.is_authenticated:
        # Obtener el nombre de usuario del usuario autenticado
        nombreUsuario = request.user.username

        # Filtrar el objeto VallEmpleado usando el nombre de usuario
        usuarioBD = VallEmpleado.objects.filter(username=nombreUsuario).first()

        # Si se encuentra un usuario en la BD y tiene una ruta de foto, actualizar la ruta de la foto
        if usuarioBD and usuarioBD.RutaFoto_ps:
        
            photo = f'http://intranet.grupo-iai.com.mx:85/SERCAPNUBE/Imagenes/FOTOS/{usuarioBD.RutaFoto_ps}'

    # Devolver la ruta de la foto
    return photo

def Categoria(request):
    usuario=None
    if request.user.is_authenticated:
        # Obtener el nombre de usuario del usuario autenticado
       nombreUsuario = request.user.username

        # Filtrar el objeto VallEmpleado usando el nombre de usuario
       usuarioBD = VallEmpleado.objects.filter(username=nombreUsuario).first()

        # Si se encuentra un usuario en la BD
       if usuarioBD:
            usuario = usuarioBD.Nombre_ct


    return usuario
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