from django.contrib import admin
from django.urls import path
from . import views
#from django.conf import settings

urlpatterns = [
    path('', views.consultar_usuarios, name="usuarios" ),
    path('agregar-usuario/', views.agregar_usuario, name='agregar_usuario')
    ]