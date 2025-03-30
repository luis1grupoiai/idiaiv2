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
"""
librerias que hacen funcionar el proyecto ;) esto es un regalo de mi para el futuro XD 02/02/2024
absl-py                       2.0.0
annotated-types               0.6.0
asgiref                       3.7.2
attrs                         23.1.0
bcrypt                        4.1.1
certifi                       2023.11.17
cffi                          1.16.0
charset-normalizer            3.3.2
click                         8.1.7
cmake                         3.27.7
colorama                      0.4.6
contourpy                     1.2.0
cryptography                  41.0.7
cycler                        0.12.1
Django                        4.2.7
django-components             0.29
django-jazzmin                2.6.0
django-mssql-backend          2.8.1
django-querycount             0.8.3
django-sslserver              0.22
django-unfold                 0.18.0
djangorestframework           3.14.0
djangorestframework-simplejwt 5.3.1
dlib                          19.24.2
dotty-dict                    1.3.1
drf-yasg                      1.21.7
face-recognition              1.3.0
face_recognition_models       0.3.0
flatbuffers                   23.5.26
fonttools                     4.46.0
gitdb                         4.0.11
GitPython                     3.1.40
gunicorn                      21.2.0
idna                          3.6
importlib-resources           6.1.1
inflection                    0.5.1
Jinja2                        3.1.2
kiwisolver                    1.4.5
ldap3                         2.9.1
markdown-it-py                3.0.0
MarkupSafe                    2.1.3
matplotlib                    3.8.2
mdurl                         0.1.2
mediapipe                     0.10.8
mssql-django                  1.3
numpy                         1.26.2
opencv-contrib-python         4.8.1.78
opencv-python                 4.8.1.78
packaging                     23.2
passlib                       1.7.4
Pillow                        10.1.0
pip                           23.3.2
protobuf                      3.20.3
psycopg2                      2.9.9
pyasn1                        0.5.1
pycparser                     2.21
pycryptodome                  3.20.0
pydantic                      2.5.3
pydantic_core                 2.14.6
Pygments                      2.17.2
PyJWT                         2.8.0
pyodbc                        5.0.1
pyparsing                     3.1.1
python-dateutil               2.8.2
python-dotenv                 1.0.0
python-gitlab                 4.3.0
python-semantic-release       8.7.0
pytz                          2023.3.post1
PyYAML                        6.0.1
requests                      2.31.0
requests-toolbelt             1.0.0
rich                          13.7.0
setuptools                    65.5.0
shellingham                   1.5.4
six                           1.16.0
smmap                         5.0.1
sounddevice                   0.4.6
sqlparse                      0.4.4
tomlkit                       0.12.3
typing_extensions             4.9.0
tzdata                        2023.3
uritemplate                   4.1.1
urllib3                       2.1.0
wfastcgi                      3.0.0
whitenoise                    6.6.0
"""
#https://www.digicert.com/kb/ssl-certificate-installation-microsoft-active-directory-ldap-2012.htm  importate parar implementar un ssl en AD
#$cert = New-SelfSignedCertificate -DnsName "active.iai.com.mx", "active" -CertStoreLocation "cert:\LocalMachine\My" codigo para crear un ssl autofirmado en el servidor AD