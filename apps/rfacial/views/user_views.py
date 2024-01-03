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
from rest_framework import status
from apps.rfacial.models import RasgosFaciales
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.files.base import ContentFile
from PIL import Image as PilImage
from PIL import Image

from django import forms
from io import BytesIO


import json
import os
import base64
import face_recognition
import cv2
import numpy as np


class CReconFacial(APIView):


    @method_decorator(csrf_exempt)
    def dispatch(self,request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    

    def get(self,request):
        datos = {'message': 'Conexion exitosa a API AUTH :)'}
    
        return JsonResponse(datos)
       
    def process_base64_image(self, image_base64):
        encoded_data = image_base64.split(',')[1]
        image = Image.open(BytesIO(base64.b64decode(encoded_data)))
        image_np = np.array(image)
        return image_np
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'imagen_base64': openapi.Schema(type=openapi.TYPE_STRING, description='Imagen en formato base64.'),
                # Otros campos que necesites
            },
            required=['imagen_base64']
        ),
        responses={200: openapi.Response('Procesamiento exitoso')}
    )

    # Este método maneja la solicitud POST y utiliza 'process_base64_image'
    def post(self, request):
        data = json.loads(request.body)
        image_base64 = data.get('imagen_base64')  # Extrae directamente la cadena base64
       
        if not image_base64:
            return JsonResponse({'status': 'error', 'message': 'No image data provided'}, status=400)

        try:
            image_np = self.process_base64_image(image_base64)
            match = self.detect_faces_dnn(image_np)
            return JsonResponse({'status': 'success', 'match': match})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
   

    # Esta función detecta rostros en la imagen y devuelve si hay una coincidencia
    def detect_faces_dnn(self, image_np):
        face_locations = face_recognition.face_locations(image_np)

        if face_locations:
            known_image = face_recognition.load_image_file("staticfiles/admin/img/10972.jpg")
            known_encoding = face_recognition.face_encodings(known_image)[0]
            unknown_encoding = face_recognition.face_encodings(image_np, known_face_locations=face_locations)[0]

            results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.5)
            match = results[0].item()  # Convierte np.bool_ a bool

        else:
            match = False

        return match


def convert_to_response_image(image_np):
    is_success, buffer = cv2.imencode(".jpg", image_np)
    return ContentFile(buffer.tobytes())

class ImageUploadForm(forms.Form): 
    image = forms.ImageField()

class CCompareFaces(APIView):   

    def extract_face_encodings(self, image):
        # Detectar las caras en la imagen
        face_locations = face_recognition.face_locations(image, model="hog")

        # Extraer los encodings de cada cara detectada
        face_encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)

        return face_encodings
    
    @staticmethod
    def extract_encodings_from_images(image_folder):
        all_encodings = []

        for filename in os.listdir(image_folder):
            if filename.lower().endswith((".jpg", ".png", ".jpeg")):
                # Separar el nombre del archivo y su extensión
                name_without_extension, _ = os.path.splitext(filename)
                
                image_path = os.path.join(image_folder, filename)
                image = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(image)

                if face_locations:
                    encodings = face_recognition.face_encodings(image, face_locations)
                    for encoding in encodings:
                        all_encodings.append((name_without_extension, encoding))
                else:
                    print(f"No se encontraron rostros en {filename}")

        return all_encodings

# Ejemplo de usocx

    def get(self, request):
         # Cargar una imagen estática desde tu servidor
         image = face_recognition.load_image_file("staticfiles/admin/img/10972.jpg")
        
         # Convertir la imagen a formato numpy
         image_np = np.array(image)

         # Extraer encodings de las caras en la imagen
         face_encodings = self.extract_face_encodings(image_np)
        
        
         db_encodings = [(rasgo.id_personal, np.array(rasgo.rasgos_faciales)) for rasgo in RasgosFaciales.objects.all()]
         if not db_encodings:
                return JsonResponse({'status': 'Database is empty'})

            # Preparar una lista de encodings de la base de datos para comparación
         db_encoding_list = [db_encoding[1] for db_encoding in db_encodings]

         TOLERANCE = 0.5  # Ajusta este valor según sea necesario
         best_match_id = None
         lowest_distance = float('inf')

         for encoding in face_encodings:
                distances = face_recognition.face_distance(db_encoding_list, encoding)
                for db_encoding, distance in zip(db_encodings, distances):
                    if distance < lowest_distance and distance < TOLERANCE:
                        lowest_distance = distance
                        best_match_id = db_encoding[0]

         if best_match_id is None:
                return JsonResponse({'status': 'No Match'})
         else:
                return JsonResponse({'status': 'Match Found', 'best_match_id': best_match_id})
            
            