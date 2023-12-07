# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import numpy as np
from django.core.files.base import ContentFile
from PIL import Image as PilImage
from PIL import Image

from django import forms
from .forms import ImageUploadForm
from io import BytesIO
import base64
import json
import face_recognition

def upload_and_detect(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']
            image_data = image_file.read()
            image = PilImage.open(BytesIO(image_data))
            image_np = np.array(image.convert('RGB'))
            image_with_faces = detect_faces_dnn(image_np)
            response_image = convert_to_response_image(image_with_faces)
            return render(request, 'result.html', {'image': response_image})
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form})



@csrf_exempt
def detect_faces_dnn(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data.get('image')
        if not image_data:
            return JsonResponse({'status': 'error', 'message': 'No image data provided'}, status=400)

        # Decodificar la imagen
        encoded_data = image_data.split(',')[1]
        image = Image.open(BytesIO(base64.b64decode(encoded_data)))
        image = np.array(image)

        # Detección de rostros con face_recognition
        face_locations = face_recognition.face_locations(image)

        if face_locations:
            # Comparación con imagen de referencia
            known_image = face_recognition.load_image_file("staticfiles/10972.jpg")
            known_encoding = face_recognition.face_encodings(known_image)[0]
            unknown_encoding = face_recognition.face_encodings(image, known_face_locations=face_locations)[0]

            results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.5)
            match = results[0].item()  # Convierte np.bool_ a bool
        else:
            match = False

        return JsonResponse({'status': 'success', 'match': match})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# Función para obtener las características ORB
def get_orb_features(img):
    orb = cv2.ORB_create()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    keypoints, descriptors = orb.detectAndCompute(gray, None)
    return keypoints, descriptors
    

# Función para comparar dos conjuntos de descriptores
def compare_images(descriptors1, descriptors2):
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    if len(descriptors1) == 0 or len(descriptors2) == 0:
        return False  # Evita división por cero si no hay descriptores
    score = len(matches) / len(descriptors1)
    return score > 0.2  # Aumenta este valor para hacer la coincidencia más estricta


@csrf_exempt
def detect_and_compare_faces(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data.get('image')

        if not image_data:
            return JsonResponse({'status': 'error', 'message': 'No image data provided'}, status=400)

        # Decodificar y cargar la imagen recibida
        encoded_data = image_data.split(',')[1]
        img = Image.open(BytesIO(base64.b64decode(encoded_data)))
        img = np.array(img)

        # Detectar rostros en la imagen recibida
        face_locations = face_recognition.face_locations(img)
        if not face_locations:
            return JsonResponse({'status': 'error', 'message': 'No faces detected'}, status=400)

        # Obtener las codificaciones faciales de la imagen recibida
        face_encodings = face_recognition.face_encodings(img, face_locations)

        # Cargar la imagen de referencia y obtener sus codificaciones
        reference_image = face_recognition.load_image_file('staticfiles/10970.jpg')
        reference_face_encoding = face_recognition.face_encodings(reference_image)[0]

        # Comparar las codificaciones faciales
        results = face_recognition.compare_faces([reference_face_encoding], face_encodings[0])
        match = results[0]

        # Preparar la imagen con los rostros detectados para responder
        for (top, right, bottom, left) in face_locations:
            # Dibujar un rectángulo alrededor de cada rostro detectado
            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', img)
        response_image = base64.b64encode(buffer).decode('utf-8')

        return JsonResponse({'status': 'success', 'image': response_image, 'match': match})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def convert_to_response_image(image_np):
    is_success, buffer = cv2.imencode(".jpg", image_np)
    return ContentFile(buffer.tobytes())

class ImageUploadForm(forms.Form): 
    image = forms.ImageField()

# Create your views here.
def inicio(request):
   return render(request, "t_inicio.html")
