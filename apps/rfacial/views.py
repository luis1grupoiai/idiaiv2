# from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# from django.http import HttpResponse
from django.http.response import JsonResponse
from apps.areas.models import *
from apps.sistemas.models import *
from passlib.hash import django_pbkdf2_sha256 as handler

from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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


    @staticmethod
    def obtenerPermisos(p_nIdSistema):
        dPermisos = []
        try:
            dPermisos = list(SistemaPermisoGrupo.objects.filter(sistema_id=p_nIdSistema).values())
        except ValueError as error:
            sTexto = "%s" % error
            print(sTexto)

        return dPermisos

    @method_decorator(csrf_exempt)
    def dispatch(self,request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    

    def get(self,request):
        # usuarios = list(User.objects.values())
        datos = {'message': 'Conexion exitosa a API AUTH :)'}
        # if len(usuarios)>0:
        #     # datos = {'message': 'Success','usuarios':usuarios}
        #     datos = {'message': 'Conexión exitosa :)'}
        # else:
        #     datos = {'message': 'Usuarios no encontrados.'}

        return JsonResponse(datos)
    
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token de autenticación.'),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario.'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='contraseña en base64.'),
                'idSistema': openapi.Schema(type=openapi.TYPE_INTEGER, description='Id del sistema donde el usuario esta iniciando sesión.'),
            },
            required=['token', 'user', 'password','idSistema']
        ),
        responses={200: 'Usuario loggeado exitosamente'},
    )
    # @action(detail=False, methods=['post'])
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
            dCamposJson = ['token', 'user', 'password','idSistema']
            sTexto = ""
            pwdD64 = ""
            dUsuario = ""
            dSistema = ""
            dPermisos = []
            password = ""
            sistema = 0
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
                if(jd['token'] == os.environ.get('SECRET_KEY')):

                    dSistema = list(Sistemas.objects.filter(id=jd['idSistema']).values())
                    if len(dSistema)>0:
                        sistema = dSistema[0]['id']
                    
                    if sistema>0:
                        #3. Decodifica el password en base64
                        pwdD64 = base64.b64decode(jd['password'])
                    
                        #Obtiene el registro del usuario mediante el userName.
                        dUsuario = list(User.objects.filter(username=jd['user'], is_active=1).values())
                        if len(dUsuario):
                            password = dUsuario[0]['password']
                    
                        #4. Verifica que la contraseña en base64 coincida con la password encriptada de BD.
                        #En caso de coincidir es como devuelve los permisos y grupos del usuario.
                        if  handler.verify(pwdD64,password):
                            # print("Las contraseñas son iguales")
                            
                            #Listado de permisos
                            # dPermisos = list(SistemaPermiso.objects.filter(sistema_id=sistema).values())
                            dPermisos = self.obtenerPermisos(sistema)
                             
                            if len(dPermisos)>0:
                                print(dPermisos)  
                            else:
                                print("Este sistema no tiene permisos")  

                            
                            datos = {'message': 'Success', 'datos': dUsuario}
                        else:
                            datos = {'message': 'Dato Invalidos', 'error':'¡Ups! la contraseña es incorrecta.'}
                    else:
                        datos = {'message': 'Dato Invalidos', 'error':'Id de sistema invalido'}                   
                else:
                    datos = {'message': 'Dato invalido.', 'error': 'El Token es incorrecto.'}
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

