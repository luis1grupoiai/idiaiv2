from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.solicitud, name='solicitud'),
    path('nuevoPersonal/', views.solicitudNuevos, name='solicitudNuevos'),
    path('enviar_correo/', views.enviar_correo, name='enviar_correo'),
    path('nuevousuario/', views.nuevosIDIAI, name='nuevousuario'),
    
    ]