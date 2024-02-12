# from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# from django.http import HttpResponse
from apps.Archivos.models import Archivo, datab, Disk , Modelos
from django.http.response import JsonResponse
#from apps.areas.models import *


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


from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


import json
import os
import base64


class CapiArchivos(APIView):
 @method_decorator(csrf_exempt)
 def dispatch(self,request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


 def get(self,request):
       
     objetos_datab = datab.objects.using("archivos")

    # Convertir los objetos a una lista de diccionarios
     lista_datab = []
     for obj in objetos_datab:
         if obj.estatus == 1 :
          objetos_datab = "Activo"
         dict_datab = {
            'nombre': obj.nombre,
            'descripcion': obj.descripcion,
            'estatus': obj.estatus,
        }
         lista_datab.append(dict_datab)
    
    # Crear el diccionario de respuesta JSON
     datos = {'message': 'JSON Valido.', "resultados": lista_datab}

    # Retornar la respuesta JSON
            # return False

     return JsonResponse(datos)  
    

    
