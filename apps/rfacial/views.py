# from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# from django.http import HttpResponse
from django.http.response import JsonResponse
from apps.areas.models import *
from passlib.hash import django_pbkdf2_sha256 as handler

from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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
                'X-CSRFToken': openapi.Schema(type=openapi.TYPE_STRING, description='Token de autenticación.'),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario.'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='contraseña en base64.'),
                'idSistema': openapi.Schema(type=openapi.TYPE_INTEGER, description='Id del sistema donde el usuario esta iniciando sesión.'),
            },
            required=['X-CSRFToken', 'user', 'password','idSistema']
        ),
        responses={200: 'Usuario loggeado exitosamente'},
    )
    def post(self,request):
        """
        Realiza la validación de las credenciales de los usuarios.

        Para realizar una creación exitosa, envía un objeto JSON con los siguientes campos:
       
        """
        #Metodo Post
        #Este metodo se encarga de validar las credenciales del ususario que se esta loggeando al sistema,
        # como resultado obtiene (mediante el userName, password, idSistema y Token) los permisos y grupos del usuario.

        try:
            #1. Carga los valores del json obtenido por el metodo post.
            jd = json.loads(request.body)
        
            #2. Decodifica el password en base64
            pwdD64 = base64.b64decode(jd['password'])

            #3. Compara el token obtenido del json contra el secretKey de la aplicación.
            if(jd['X-CSRFToken'] == os.environ.get('SECRET_KEY')):
                
                #4. Obtiene el registro del usuario mediante el userName.
                dUsuario = list(User.objects.filter(username=jd['user']).values())
                password = dUsuario[0]['password']
            
                #4. Verifica que la contraseña desencriptada en base64 coincida con la password encriptada de BD.
                #En caso de coincidir es como devuelve los permisos y grupos del usuario.
                if  handler.verify(pwdD64,password):
                    print("Las contraseñas son iguales")
                    datos = {'message': 'Success', 'datosUser': dUsuario}
                else:
                    datos = {'message': 'Ups, la contraseña es incorrecta.'}
        
            return JsonResponse(datos)
        except ValueError as error:
            print("invalid json: %s" % error)
            return False
        

    # def put(self,request):
    #     pass

    # def delete(self,request):
    #     pass

    

