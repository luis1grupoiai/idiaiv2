from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse
# from camera import VideoCamera, IPWebCam
import numpy as np
import cv2
import os, urllib
import mediapipe as mp




def gen_frame():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # while True:
    while cap.isOpened():
        
        ret, frame = cap.read()
        frame_flip = cv2.flip(frame,1)

        if not ret:
            print("No hay imagen.")
            break
        else:
            print("Si se obtiene imagen de camara.")
            # cv2.imshow("Video", frame)
            # suc, encode = cv2.imencode('.jpg', frame)
            # frame = encode.tobytes()

            if cv2.waitKey(1) & 0xFF == ord("s"):
                break


        # yield(b'--frame\r\n' 
        #       b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n\r\n')

# Create your views here.
def inicio(request):
    return render(request, "facial.html")


def video(request):
    # return HttpResponse(gen_frame(),mime='multipart/x-mixed-replace; boundary=frame')
    return StreamingHttpResponse(gen_frame(), content_type ='multipart/x-mixed-replace; boundary=frame')