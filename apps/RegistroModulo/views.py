from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import TRegistroDeModulo 
from apps.AsignarUsuario.models import  TRegistroAccionesModulo ,VallEmpleado
from .forms import ModuloForm
from django.contrib.auth.decorators import login_required , user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib import messages
from .mixins import SuperuserRequiredMixin , SuperuserRedirectMixin
from django.contrib.auth.models import User
from django.conf import settings
from config.logger_setup import LoggerSetup
import os

entorno = os.environ.get('DJANGO_ENV')

logger = LoggerSetup.setup_logger_for_environment('RegistroModulo', entorno)


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
        logger.info(f"Usuario {self.request.user.username} accediendo a lista de módulos")
        context = super().get_context_data(**kwargs)
        context['verificar'] = ModuloEntrada
        context['desarrollo']=settings.DEBUG   #LINEA PARA QUE APAREZCA EL BOTON DE ELIMINAR 
        return context

class ModuloCreateView(LoginRequiredMixin,NombreUsuarioMixin,SuperuserRedirectMixin,CreateView):
    model = TRegistroDeModulo
    form_class = ModuloForm
    template_name = 'modulo_form.html'
    success_url = reverse_lazy('modulo_list')
    
    def get_context_data(self, **kwargs):
       logger.info(f"Usuario {self.request.user.username} accediendo al formulario de creación de módulo")
       context = super().get_context_data(**kwargs)
       context['verificar'] = ModuloEntrada
       return context   
    
    
    def form_valid(self, form):
        logger.info(f"Usuario {self.request.user.username} intentando crear un nuevo módulo")
        try:
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
            
            logger.info(f"Módulo {self.object.nombre} creado exitosamente por {nombreUsuario}")
            return response
        except Exception as e:
            logger.error(f"Error al crear módulo: {str(e)}")
            raise

class ModuloUpdateView(LoginRequiredMixin,NombreUsuarioMixin,SuperuserRequiredMixin,UpdateView):
    model = TRegistroDeModulo
    form_class = ModuloForm
    template_name = 'modulo_form.html'
    success_url = reverse_lazy('modulo_list')
      
    def get_initial(self):
        initial = super().get_initial()
        # Obtén la instancia del módulo que se va a actualizar
        modulo = self.get_object()
        logger.info(f"Usuario {self.request.user.username} accediendo a formulario de actualización para módulo {modulo.nombre}")
        # Establece los valores iniciales desencriptados para el formulario
        initial['nombre'] = modulo.nombre
        initial['descripcion'] = modulo.descripcion
        return initial
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verificar'] = ModuloEntrada
        return context    
    

    def form_valid(self, form):
        modulo = self.get_object()
        logger.info(f"Usuario {self.request.user.username} intentando actualizar el módulo {modulo.nombre}")
        
        # Validación para el nombre
        if form.cleaned_data['nombre'] != modulo.nombre:
           logger.warning(f"Intento de cambiar el nombre del módulo {modulo.nombre} a {form.cleaned_data['nombre']} por {self.request.user.username}")
           messages.error(self.request, 'No puedes cambiar el nombre del módulo.')
           return self.form_invalid(form)
       
        # Validación para la descripción
        descripcion = form.cleaned_data.get('descripcion')
        if not descripcion:
            logger.warning(f"Intento de actualizar el módulo {modulo.nombre} con descripción vacía por {self.request.user.username}")
            messages.error(self.request, 'La contraseña no puede estar vacía.')
            return self.form_invalid(form)
        
        try:
            # Procesamiento normal si todas las validaciones pasan
            response = super(ModuloUpdateView, self).form_valid(form)
            # Obtén la información del usuario y otros detalles aquí
            nombreUsuario = self.request.user.get_full_name()  # O tu método personalizado

            # Insertar el registro de acción
            insertar_registro_accion(
                nombreUsuario,
                'Modulo',
                'Editar',
                f"Se Modifico  el módulo {self.object.nombre}",
                get_client_ip(self.request),
                self.request.META.get('HTTP_USER_AGENT'),
                'N/A'
            )
            
            logger.info(f"Módulo {self.object.nombre} actualizado exitosamente por {nombreUsuario}")
            
            #actualiza la contraseña 
            #Inicio ---- codigo para cambiar la contraseña en el repositorio del IDIAI : 
            try:
                user = User.objects.get(username=self.object.nombre)
                user.set_password(self.object.descripcion)# Asegúrate de que la contraseña esté en texto plano aquí
                
                user.save()
                
                insertar_registro_accion(
                        nombreUsuario,
                        'Modulo',
                        'Actualizó',
                        f"Se Actualizó la contraseña del usuario. '{self.object.nombre}' en el IDIAI V2 ",
                        get_client_ip(self.request),
                        self.request.META.get('HTTP_USER_AGENT'),
                        'N/A'
                        )
                imprimir(f"Se actualizo la contraseña de IDIAI V2  {self.object.nombre} ")
                logger.info(f"Contraseña actualizada en IDIAI V2 para el usuario {self.object.nombre}")
            except User.DoesNotExist:
                logger.error(f"No se encontró el usuario {self.object.nombre} en el repositorio IDIAI")
                imprimir(f"Error: Usuario {self.object.nombre} no encontrado en repositorio IDIAI")
            except Exception as e: 
                logger.error(f"Error al guardar la contraseña en repositorio IDIAI para {self.object.nombre}: {str(e)}")
                imprimir(f"Error al guardar el registro en repositorios de IDIAI {self.object.nombre} : {e}")
            
            return response
        except Exception as e:
            logger.error(f"Error al actualizar módulo {modulo.nombre}: {str(e)}")
            raise
    

class ModuloDeleteView(LoginRequiredMixin,NombreUsuarioMixin,SuperuserRequiredMixin,DeleteView):
    model = TRegistroDeModulo
    template_name = 'modulo_confirm_delete.html'
    success_url = reverse_lazy('modulo_list')
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        logger.info(f"Usuario {request.user.username} accediendo a la página de confirmación para eliminar el módulo {self.object.nombre}")
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        self.object = self.get_object()
        logger.info(f"Usuario {self.request.user.username} intentando eliminar el módulo {self.object.nombre}")
        try:
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
            
            logger.info(f"Módulo {self.object.nombre} eliminado exitosamente por {nombreUsuario}")
            return response
        except Exception as e:
            logger.error(f"Error al eliminar módulo {self.object.nombre}: {str(e)}")
            raise

@login_required  
@user_passes_test(es_superusuario) # Solo permitir a superusuarios
def bitacora(request):
    logger.info(f"Usuario {request.user.username} accediendo a la bitácora de módulos")
    
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
    logger.debug(f"Accediendo a la vista de detalle del registro con ID: {id}")
    try:
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
        
        logger.info(f"Usuario {request.user.username} visualizó detalles del módulo {registro.nombre}")
          
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
    except Exception as e:
        logger.error(f"Error al acceder al detalle del registro {id}: {str(e)}")
        raise

def insertar_registro_accion(nombre_usuario, modulo, nombre_accion, descripcion, ip_usuario, user_agent, browser_id):
    try:
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
        logger.info(f"Registro de acción creado: {modulo}/{nombre_accion} por {nombre_usuario}")
        print(nuevo_registro)
    except Exception as e:
        logger.error(f"Error al insertar registro de acción: {str(e)}")
    
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

        try:
            # Filtrar el objeto VallEmpleado usando el nombre de usuario
            usuarioBD = VallEmpleado.objects.filter(username=nombreUsuario).first()

            # Si se encuentra un usuario en la BD y tiene una ruta de foto, actualizar la ruta de la foto
            if usuarioBD and usuarioBD.RutaFoto_ps:
                photo = f'https://intranet.grupo-iai.com.mx:330/SERCAPNUBE/Imagenes/FOTOS/{usuarioBD.RutaFoto_ps}'
        except Exception as e:
            logger.error(f"Error al obtener foto de usuario {nombreUsuario}: {str(e)}")

    # Devolver la ruta de la foto
    return photo

def Categoria(request):
    usuario=None
    if request.user.is_authenticated:
        # Obtener el nombre de usuario del usuario autenticado
        nombreUsuario = request.user.username

        try:
            # Filtrar el objeto VallEmpleado usando el nombre de usuario
            usuarioBD = VallEmpleado.objects.filter(username=nombreUsuario).first()

            # Si se encuentra un usuario en la BD
            if usuarioBD:
                usuario = usuarioBD.Nombre_ct
        except Exception as e:
            logger.error(f"Error al obtener categoría de usuario {nombreUsuario}: {str(e)}")
            
    return usuario

def imprimir(mensaje): #funcion para imprimir en la consola  en modo desarrollador 
    if settings.DEBUG:
        print(mensaje)
        logger.debug(mensaje)