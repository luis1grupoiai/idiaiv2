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
            known_image = face_recognition.load_image_file("static/admin/img/10972.jpg")
            known_encoding = face_recognition.face_encodings(known_image)[0]
            unknown_encoding = face_recognition.face_encodings(image, known_face_locations=face_locations)[0]

            results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.5)
            match = results[0].item()  # Convierte np.bool_ a bool
        else:
            match = False

        return JsonResponse({'status': 'success', 'match': match})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



def convert_to_response_image(image_np):
    is_success, buffer = cv2.imencode(".jpg", image_np)
    return ContentFile(buffer.tobytes())

class ImageUploadForm(forms.Form): 
    image = forms.ImageField()

# Create your views here.
def inicio(request):
   return render(request, "t_inicio.html")
