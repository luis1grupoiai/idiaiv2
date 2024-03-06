from django.contrib import admin
from django.urls import path
from . import views
#from django.conf import settings

urlpatterns = [
    path('', views.importar_usuarios, name='importarusuarios'),
    path('importar_modulos/', views.importarmodulo, name='importarmodulos'),
    
    ]