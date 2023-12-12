from django.contrib import admin
from django.urls import path
from . import views
#from django.conf import settings

urlpatterns = [
    path('consultar_usuarios/', views.consultar_usuarios, name="usuarios" ),
    path('agregar-usuario/', views.agregar_usuario, name='agregar_usuario'),
    path('editar_usuario/', views.editar_usuario, name='editar_usuario'),
    path('consultar_usuarios/activar_usuario/<str:nombre_usuario>/', views.activar_usuario, name='activar_usuario'),
    path('consultar_usuarios/desactivar_usuario/<str:nombre_usuario>/', views.desactivar_usuario, name='desactivar_usuario'),
    path('', views.home, name='home'),
    path('logout/',views.salir,name = 'salir')
    ]