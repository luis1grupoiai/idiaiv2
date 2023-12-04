# from django.shortcuts import render, redirect
from django.views import View
# from django.http import HttpResponse
from django.http.response import JsonResponse
# from camera import VideoCamera, IPWebCam
# import numpy as np
# import cv2
# import os, urllib
# import mediapipe as mp


class CAutenticacion(View):

    def get(self,request):
        datos = {'message': 'Success'}
        return JsonResponse(datos)

    def post(self,request):
        datos = {'message': 'Success'}
        return JsonResponse(datos)

    def put(self,request):
        pass

    def delete(self,request):
        pass