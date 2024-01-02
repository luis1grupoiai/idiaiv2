from django.urls import path
from. import views


urlpatterns = [
    path('', views.inicio, name='upload'),
    path('detect_faces/', views.detect_faces_dnn, name='detect_faces_dnn'),
    
]