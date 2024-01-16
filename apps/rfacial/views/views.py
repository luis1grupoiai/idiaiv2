# from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# from django.http import HttpResponse
from django.db import models
from django.http.response import JsonResponse
from apps.areas.models import *
from apps.sistemas.models import *
from apps.rfacial.models import *
from apps.AsignarUsuario.models import *
from passlib.hash import django_pbkdf2_sha256 as handler

from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils import timezone


from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from apps.mycore.views.ejecutarsp import CEjecutarSP


import json
import os
import base64
# from camera import VideoCamera, IPWebCam
# import numpy as np
# import cv2
# import os, urllib
# import mediapipe as mp

# def swagger_json(request):
#         with open('swagger/apiAuth.json', 'r') as json_file:
#             data = json.load(json_file)
#         return JsonResponse(data)

class CAutenticacion(APIView):
        
    oExecSP = CEjecutarSP()
    sNombreSistema = ""

    # @staticmethod
    def obtenerPermisos(self, p_nIdSistema, p_nIdUsuario):
        dPermisos = {}
        dPermisosUsuario = {}
        print("Accede a metodo obtenerPermisos.")
        try:
            # dPermisos = list(SistemaPermisoGrupo.objects.filter(sistema_id=p_nIdSistema, permiso_id__isnull=False).values())
            self.oExecSP.registrarParametros("idUsuario",p_nIdUsuario)
            self.oExecSP.registrarParametros("idSistema",p_nIdSistema)
            dPermisos = self.oExecSP.ejecutarSP("obtenerPermisosUsuario")

            # print("el tipo de dato es: ")
            # print(type(dPermisos))

            if len(dPermisos)>0:
                # print("El usuario si tiene acceso al sistema con clave: "+ str(p_nIdSistema))
                # print(dPermisos[0][12])
                # self.sNombreSistema = dPermisos[0][13]
                for dPermiso in dPermisos:
                    dPermisosUsuario[dPermiso[6]] = dPermiso[7]

                # print(dPermisosUsuario)

            
        except ValueError as error:
            sTexto = "Error en el metodo obtenerPermisos: %s" % error
            print(sTexto)

        return dPermisosUsuario
    

    def obtenerDatosPersonales(self, p_nIdUsuario=0, p_nIdPersonal=0):
        dDatos = {}
        # dDatosUsuario = {}
        print("Accede a metodo obtenerDatosPersonales.")
        try:
            
            if p_nIdUsuario>0:
                self.oExecSP.registrarParametros("idUsuario",p_nIdUsuario)
            elif p_nIdPersonal>0:
                self.oExecSP.registrarParametros("idPersonal",p_nIdPersonal)
            
            dDatos = self.oExecSP.ejecutarSP("obtenerDatosPersonales")

            # if len(dDatos)>0:
            #    dDatosUsuario = dDatos
                

                # print(dPermisosUsuario)           
        except ValueError as error:
            sTexto = "Error en el metodo obtenerDatosPersonales: %s" % error
            print(sTexto)

        return dDatos

    def obtenerGrupos(self, p_nIdSistema, p_nIdUsuario):
        dGrupos = {}
        dGruposUsuario = {}
        print("Accede a metodo obtenerGrupos.")
        try:
            # dPermisos = list(SistemaPermisoGrupo.objects.filter(sistema_id=p_nIdSistema, permiso_id__isnull=False).values())
            self.oExecSP.registrarParametros("idUsuario",p_nIdUsuario)
            self.oExecSP.registrarParametros("idSistema",p_nIdSistema)
            dGrupos = self.oExecSP.ejecutarSP("obtenerGruposUsuario")

            # print("el tipo de dato es: ")
            # print(type(dGrupos))

            if len(dGrupos)>0:
                # print("El usuario si tiene acceso al sistema con clave: "+ str(p_nIdSistema))
                # print(dPermisos[0][12])
                # self.sNombreSistema = dGrupos[0][16]
                for dGrupo in dGrupos:
                    # sNombreGrupo = dGrupo[9]
                    dGruposUsuario[dGrupo[15]] = dGrupo[13]
                    

                    #Método encargado de ordenar los permisos por grupos en su correspondiente bloque
                    #Se entregan los permisos de grupo dentro del bloque permisos, ya grupos no tendra un bloque propio
                    #en la respuesta JSON de la api - 15/12/2023
                    # dGruposUsuario = self.ordenarGrupos(sNombreGrupo,dGrupos)

                # print(dGruposUsuario)

            
        except ValueError as error:
            sTexto = "Error en el metodo obtenerGrupos: %s" % error
            print(sTexto)

        return dGruposUsuario
    
    def ordenarGrupos(self,p_sElementoBuscado, p_dlistas):
        try:
            listas_coincidentes = []
            dGrupoOrdenado = {}
            dGrupoUsuario = {}

            if len(p_sElementoBuscado)>0:
                listas_coincidentes = [lista for lista in p_dlistas if p_sElementoBuscado in lista]
                # print("Listas con el elemento coincidente:", listas_coincidentes)
                
                if len(listas_coincidentes)>0:
                    for dGrupo in listas_coincidentes:
                        dGrupoOrdenado[dGrupo[15]] = dGrupo[13]


                dGrupoUsuario[p_sElementoBuscado] = dGrupoOrdenado

                # print(dGrupoUsuario)

            else:
                print("El nombre del grupo no es el correcto.")
        except ValueError as error:
            sTexto = "Error en el metodo ordenarGrupos: %s" % error
            print(sTexto)

        return dGrupoUsuario

    def get_custom_auth_token(self, p_sUsuario, p_sTiempoExp = 3):
        # Generamos token para autenticación del usuario :) 
        sTexto = ""
        sToken_encoded = ""
        expiration_time= 0
        expiration_hours = int(p_sTiempoExp) # 3 horas por defecto en caso de que no se asigne un tiempo en la app.

        try:
            user = User.objects.get(username=p_sUsuario) 
            timestamp = int(timezone.now().timestamp())

            # Calcular la fecha de expiración del token
            expiration_time = timestamp + (expiration_hours * 3600)  # 3600 segundos en una hora
            # expiration_time = timestamp + (expiration_hours * 60)  # 60 segundos en un minuto, solo para terminos de prueba ...
            
            token = default_token_generator.make_token(user)+ ',' + str(expiration_time)
   
            sToken_encoded = urlsafe_base64_encode(force_bytes(token))

        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'Ocurrió un error al generar el token para el usuario. ', "error": sTexto}

        # print(type(sToken_encoded))
        return sToken_encoded



    @staticmethod
    def prueba():
        print("Accede a metodo prueba...")
        

       
        # instancia.registrarParametros("idUsuario",2)
        # sSP = "obtenerPermisosUsuario"
        # instancia.registrarParametros("usuario","ana.sanchez")
        # instancia.registrarParametros("edad","14")

        # resultado = instancia.ejecutarSP(sSP)

    @method_decorator(csrf_exempt)
    def dispatch(self,request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    

    def get(self,request):
        # usuarios = list(User.objects.values())
        datos = {'message': 'Conexion exitosa a API AUTH :)'}
        # dDatosPersonales = self.obtenerDatosPersonales("2")

        # empleados = VallEmpleado.objects.filter(id=2)
        # self.prueba()
        # if len(usuarios)>0:
        #     # datos = {'message': 'Success','usuarios':usuarios}
        #     datos = {'message': 'Conexión exitosa :)'}
        # else:
        #     datos = {'message': 'Usuarios no encontrados.'}

        return JsonResponse(datos)
    
    # @action(detail=True, methods=['post'])
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Llave que identifica el sistema, en base 64.'),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario.'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='contraseña en base64.'),
                'idSistema': openapi.Schema(type=openapi.TYPE_INTEGER, description='Id del sistema donde el usuario esta iniciando sesión.'),
                'timeExp': openapi.Schema(type=openapi.TYPE_INTEGER, description='Número de horas de la vigencia del token; si número de horas es 0, entonces por default el token durara 3 hrs.'),
            },
            required=['token', 'user', 'password','idSistema','timeExp']
        ),
        responses={200: 'Usuario loggeado exitosamente'},
    )    
    def post(self,request):
        """
        Realiza la validación de las credenciales de los usuarios.

        Para realizar un consulta exitosa, envía un objeto JSON con los siguientes campos:
       
        """
        #Metodo Post
        #Este metodo se encarga de validar las credenciales del ususario que se esta loggeando al sistema,
        # como resultado obtiene (mediante el userName, password, idSistema y Token) los permisos y grupos del usuario.

        try:
            #1. Carga los valores del json obtenido por el metodo post.
            jd = json.loads(request.body)
          
            
            #Declaración y asignación de variables
            bValido = True
            dCamposJson = ['token', 'user', 'password','idSistema', 'timeExp']
            sTexto = ""
            pwdD64 = ""
            dUsuario = ""
            dSistema = ""
            dDatosPersonales = {}
            dPermisos = {}
            dGrupos = {}
            password = ""
            sistema = 0
            idPersonal = 0
            sNombreCompleto = ""
            sUserName = ""
            tokenApi = ""
            nItemJson = 0
            keySis = ""
            #total de items permitidos en la API, definidos en la diccionario dCamposJson
            nLenDef = len(dCamposJson) 
            #Variable que almacenara el numero de items del json recibido por la API.
            numero_de_items = 0 
            

            #Valida que el numero de claves del JSON enviado a la API
            #coincida con el numero de claves declaras en el diccioario dCamposJson
            nItemJson = len(jd)
            
            if nItemJson != nLenDef:
                sTexto = "El tamaño del JSON obtenido no es el esperado, por favor de verificar. "
                bValido = False



            #Validación de las claves json, si alguna clave no se encuentra en el objeto, entonces
            #el valor de bValido es Falso y regresa un mensaje de error indicando el identificador
            #  faltante.
            for item in dCamposJson:
                if item in jd:
                    continue
                else:
                    sTexto += "El campo faltante es: "+item+". "
                    bValido = False
                    break
            
            #si las claves estan correctas, continuara realizando el resto del proceso
            # de autenticación
            if bValido:

                #2. Compara el token obtenido del json contra el secretKey de la aplicación.
                # 2.1. Para el sistema de RF (Reconocimiento Facial) el  token =4  - KEY_RF
                keySis = base64.b64decode(jd['token'])
                keySis = keySis.decode('utf-8')

                # print(keySis)
                # print(os.environ.get('KEY_RF'))
               
                 
                if((keySis == os.environ.get('SECRET_KEY')) or (keySis == os.environ.get('KEY_RF'))):
                   
                    #Valida si el sistema existe en el catalogo de sistemas.
                    dSistema = list(Sistemas.objects.filter(id=jd['idSistema']).values())
                    if len(dSistema)>0:
                        sistema = dSistema[0]['id']
                        self.sNombreSistema = dSistema[0]['nombre']
                    
                    #Si el sistema obtenido se encuentra en el catalogo de sistemas y el sistema no es el sistema 4 (RF)
                    if sistema>0 and keySis!=os.environ.get('KEY_RF'):
                      
                        #3. Decodifica el password en base64
                        pwdD64 = base64.b64decode(jd['password'])
                    
                        #Obtiene el registro del usuario mediante el userName.
                        dUsuario = list(User.objects.filter(username=jd['user'], is_active=1).values())
                       
                        if len(dUsuario):
                            password = dUsuario[0]['password']
                            idUsuario = dUsuario[0]['id']
                       
                        #4. Verifica que la contraseña en base64 coincida con la password encriptada de BD.
                        #En caso de coincidir es como devuelve los permisos y grupos del usuario.
                        if  handler.verify(pwdD64,password):
                            # print("Las contraseñas son iguales")
                            
                            #Listado de permisos
                            # dPermisos = list(SistemaPermiso.objects.filter(sistema_id=sistema).values())
                            dDatosPersonales = self.obtenerDatosPersonales(idUsuario,0)
                            if len(dDatosPersonales)>0:
                                print(dDatosPersonales[0][1])
                                idPersonal = dDatosPersonales[0][1]
                                sNombreCompleto = dDatosPersonales[0][8]

                                dPermisos = self.obtenerPermisos(sistema,idUsuario)
                                dGrupos = self.obtenerGrupos(sistema,idUsuario)

                                #El listado de permisos de grupos se unen al bloque permisos, todo junto.
                                dPermisos.update(dGrupos)
                                # resultados = vUsuarioPermiso.objects.all()

                                # if len(dPermisos)>0:
                                #     print("resultados :) ")  
                                    
                                # else:
                                
                                #     sTexto += "Este sistema no tiene permisos"

                                
                                # datos = {'message': 'Success', 'datos': dUsuario}
                                # datos = {'message': 'Success', 'sistema':self.sNombreSistema,'permisos': dPermisos, 'grupos':dGrupos}
                                # token, created = Token.objects.get_or_create(username=jd['user'])
                                if jd['timeExp'] == 0:
                                    print("El tiempo de expiración es 0, por lo tanto por default el token durara 3 horas.")
                                    tokenApi = self.get_custom_auth_token(jd['user'])
                                else:
                                    print("El tiempo de expiración no es igual 0, por lo tanto por default el token durara "+str(jd['timeExp'])+" horas.")
                                    tokenApi = self.get_custom_auth_token(jd['user'],jd['timeExp'])

                                # print(tokenApi)

                                # is_token_valid = default_token_generator.check_token(jd['user'], tokenApi)
                                
                                datos = {'message': 'Success','idPersonal':idPersonal,'usuario': jd['user'], 'password': jd['password'],'sistema':self.sNombreSistema,'nombreCompleto':sNombreCompleto,'token': tokenApi,'permisos': dPermisos}
                            else:
                                datos = {'message': 'Sin datos', 'error':'¡Ups! Al parecer no existen registros de este usuario, por favor de verificar los datos proporcionados. '}

                        else:
                            datos = {'message': 'Dato Invalidos', 'error':'¡Ups! la contraseña es incorrecta.'}

                    elif  sistema>0 and keySis==os.environ.get('KEY_RF'):

                        print("Petición recibida por parte del API de reconocimiento facial.")

                        idPersonal = int(jd['user'])
                        dDatosPersonales = self.obtenerDatosPersonales(0,idPersonal)

                        if len(dDatosPersonales)>0:
                                print(dDatosPersonales[0][1])
                                idUsuario = dDatosPersonales[0][0]
                                sNombreCompleto = dDatosPersonales[0][8]
                                password = dDatosPersonales[0][3]
                                sUserName = dDatosPersonales[0][2]

                                dPermisos = self.obtenerPermisos(sistema,idUsuario)
                                dGrupos = self.obtenerGrupos(sistema,idUsuario)

                                dPermisos.update(dGrupos)

                                # tokenApi = self.get_custom_auth_token(sUserName)

                                # print(tokenApi)

                                if jd['timeExp'] == 0:
                                    print("El tiempo de expiración es 0, por lo tanto por default el token durara 3 horas.")
                                    tokenApi = self.get_custom_auth_token(sUserName)
                                else:
                                    print("El tiempo de expiración no es igual 0, por lo tanto por default el token durara "+str(jd['timeExp'])+" horas.")
                                    tokenApi = self.get_custom_auth_token(sUserName,jd['timeExp'])

                                datos = {'message': 'Success','idPersonal':idPersonal,'usuario': sUserName, 'password': password,'sistema':self.sNombreSistema,'nombreCompleto':sNombreCompleto,'token': tokenApi,'permisos': dPermisos}
                        else:
                                datos = {'message': 'Sin datos', 'error':'¡Ups! Al parecer no existen registros de este usuario, por favor de verificar los datos proporcionados. '}
                    else:
                        datos = {'message': 'Dato Invalidos', 'error':'Id de sistema invalido'}                   
                else:
                    datos = {'message': 'Dato invalido.', 'error': 'El key del sistema es incorrecto.'}
            else:
                datos = {'message': 'JSON invalido.', 'error': sTexto}
            
        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'JSON invalido. ', "error": sTexto}
            # return False
        

        return JsonResponse(datos)
    
    
    # def put(self,request):
    #     pass

    # def delete(self,request):
    #     pass


class Protegida(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        
        datos = {'content': 'Esta vista está protegida'}
        # return Response({"content": "Esta vista está protegida"})  
        return JsonResponse(datos)  

class CVerificaToken(APIView):

    # # def is_token_expired(self, user, token, expiration_hours=24):
    # def is_token_expired(self, token, expiration_hours=5):
        
    #     # Verificar si el token ha expirado
    #      # Obtener la fecha de creación del token del mismo
    #     timestamp = default_token_generator._timestamp_from_token(token)

    #     # Calcular la fecha de expiración del token
    #     # expiration_time = timestamp + (expiration_hours * 3600)  # 3600 segundos en una hora
    #     expiration_time = timestamp + (expiration_hours * 60)  # 60 segundos prueba de 1 minuto...

    #     # Verificar si el token ha expirado
    #     return expiration_time > timezone.now().timestamp()



    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token asignado por la aplicación.'),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario.')
            },
            required=['token', 'user']
        ),
        responses={200: 'Token Validado'},
    ) 
    def post(self,request):
        """
        Realiza la validación del token dado por la api de autenticación.

        Para realizar un consulta exitosa, envía un objeto JSON con los siguientes campos:
       
        """
        try:
            bValido = True
            sToken_encoded = ""
            sUserName = ""
            tk = ""
            is_token_valid = False
            is_token_expired = True
            sTexto = ""
            nLenDef = 0
            nItemJson = 0
            # expiration_hours = 1 #TODO: ✍ Tiempo de expiración de token por defecto son 5 horas, pero tratar de ver la manera de hacerlo configurable...

            dCamposJson = ['token', 'user']
            
            jd = json.loads(request.body)

            nLenDef = len(dCamposJson) 

            nItemJson = len(jd)
            
            if nItemJson != nLenDef:
                sTexto = "El tamaño del JSON obtenido no es el esperado, por favor de verificar. "
                bValido = False

            for item in dCamposJson:
                if item in jd:
                    continue
                else:
                    sTexto += " El campo faltante es: "+item+". "
                    bValido = False
                    break

            if bValido:

                sToken_encoded = jd['token']
                sUserName = jd['user']
                
                user = User.objects.get(username=sUserName) 
                
                tk = urlsafe_base64_decode(sToken_encoded)                
                tk = tk.decode('utf-8')
                print(tk)
                 # Separar el token y la marca de tiempo
                parts = tk.split(',')

                print("Token ... :( por favor funciona: ")
                print(parts[0])
                
                token_without_timestamp = '-'.join(parts[:-1])
                timestamp = int(parts[-1])
                print("timestamp: ")
                print(timestamp)

                # Calcular la fecha de expiración del token
                # expiration_time = timestamp + (expiration_hours * 3600)  # 3600 segundos en una hora
                expiration_time = timestamp  # 3600 segundos en una hora
                # expiration_time = timestamp + (1 * 60)  # 60 segundos prueba de 1 min.

                if expiration_time > timezone.now().timestamp():
                    print("Aun no expira el token")
                    is_token_expired = False
                else:
                    print("El token ya expiro...")
                    # is_token_expired = True

                # is_token_valid = default_token_generator.check_token(user, tk)
                is_token_valid = default_token_generator.check_token(user, parts[0])
                

                if is_token_valid and not is_token_expired:
                    print("El token es válido y no ha expirado para este usuario...")
                    # is_token_expired = self.is_token_expired(tk)
                    # print(type(is_token_expired))

                    datos = {'message': 'Success', "descripcion":'El token es válido y no ha expirado.'}
                else:
                    datos = {'message': 'Error', "descripcion":'El token ya no es válido y posiblemente ya expiro'}
                    print("El token no es válido.")
            else:
                datos = {'message': 'Datos Invalidos ', 'Error': sTexto}


            
         
            # is_token_valid = default_token_generator.check_token(user, token)

            

        except ValueError as error:
            sTexto = "%s" % error
            datos = {'message': 'JSON invalido. ', "error": sTexto}
            # return False

        return JsonResponse(datos)  
    
    def get(self,request):
        print("")