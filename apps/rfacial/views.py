# from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# from django.http import HttpResponse
from django.http.response import JsonResponse
from apps.areas.models import *
from passlib.hash import django_pbkdf2_sha256 as handler

import json
import os
import base64
# from camera import VideoCamera, IPWebCam
# import numpy as np
# import cv2
# import os, urllib
# import mediapipe as mp


class CAutenticacion(View):

    @method_decorator(csrf_exempt)
    def dispatch(self,request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self,request):
        usuarios = list(User.objects.values())

        if len(usuarios)>0:
            datos = {'message': 'Success','usuarios':usuarios}
        else:
            datos = {'message': 'Usuarios no encontrados.'}

        return JsonResponse(datos)

    def post(self,request):
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
                    datos = {'message': 'Ups, parece ser que los tokens no coinciden.'}
        
            return JsonResponse(datos)
        except ValueError as error:
            print("invalid json: %s" % error)
            return False
        

    def put(self,request):
        pass

    def delete(self,request):
        pass