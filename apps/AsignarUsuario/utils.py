from django.conf import settings
from apps.AsignarUsuario.models import VallEmpleado


class AtributosDeEmpleado: 
    @staticmethod
    def Categoria(request): # funcion para obtener la categoria del empleado 
        usuario=None
        if request.user.is_authenticated:
                # Obtener el nombre de usuario del usuario autenticado
            nombreUsuario = request.user.username

                # Filtrar el objeto VallEmpleado usando el nombre de usuario
            usuarioBD = VallEmpleado.objects.filter(username=nombreUsuario).first()

                # Si se encuentra un usuario en la BD
            if usuarioBD:
                    usuario = usuarioBD.Nombre_ct


        return usuario #devuelve la categoria del empleado 

    @staticmethod
    def photoUser(request):# funcion para obtener la foto del empleado 
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
            
                photo = f'https://intranet.grupo-iai.com.mx:330/SERCAPNUBE/Imagenes/FOTOS/{usuarioBD.RutaFoto_ps}'

        # Devolver la ruta de la foto
        return photo
    @staticmethod
    def nameUser(request):# funcion para obtener el nombre del empleado 
        if request.user.is_authenticated:
            nombreUsuario = request.user.first_name+" "+request.user.last_name 
        
        return  nombreUsuario
    @staticmethod
    def imprimir(mensaje): #funcion para imprimir en la consola 
        if settings.DEBUG:
            print(mensaje)



class IPSinBaseDatos:
    def __init__(self, id='0', server='ldaps://', ip='0.0.0.0'):
        self.id = id
        self.server = server
        self.ip = ip

    def cambiar_ip(self, nueva_ip):
        self.ip = nueva_ip

    def mostrar_info(self):
        print(f"ID: {self.id}, Servidor: {self.server}, IP: {self.ip}")
        
        
        
        
        
        
        