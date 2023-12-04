from django.urls import path
from .views import CAutenticacion

urlpatterns = [
    # path('facial/', views.inicio, name='inicio'),
    # path('video/', views.video, name='video'),
    # path('webcam/', views.webcam, name='webcam'),
    path('auth/', CAutenticacion.as_view(), name='auth')
]