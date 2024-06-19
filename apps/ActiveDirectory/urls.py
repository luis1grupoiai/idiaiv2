from django.contrib import admin
from django.urls import path
from . import views
#from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('ajax_login/', views.Verificarlogin, name='verificarlogin'),
    path('consultar_usuariosID/', views.consultarUsuariosIDIAI, name="usuariosID" ),
    path('consultar_usuarios/', views.consultar_usuarios, name="usuarios" ),
    path('agregar_usuario/', views.agregar_usuario, name='agregar_usuario'),
    path('editar_usuario/', views.editar_usuario, name='editar_usuario'),
    path('consultar_usuarios/activar_usuario/<str:nombre_usuario>/', views.activar_usuario, name='activar_usuario'),
    path('consultar_usuarios/desactivar_usuario/<str:nombre_usuario>/', views.desactivar_usuario, name='desactivar_usuario'),
    path('verificar-usuario/<str:nombre_usuario>/', views.verificar_usuario, name='verificar_usuario'),
    path('modulo-usuario/', views.key_usuario, name='modulo-usuario'),
    path('modulo-update/', views.update_usuario, name='modulo-update'),
    path('bitacora/', views.bitacora, name="bitacora" ),
    path('ipconfig/', views.ipconfig, name = "ipconfig"),
    path('personalNoContratada/', views.personalNoContratada, name='personalNoContratada'),
    path('actualizarPD/', views.actualizarProyectoDireccion, name='ActProyectoDireccion'),
    path('logout/',views.salir,name = 'salir')
    
    
    ]