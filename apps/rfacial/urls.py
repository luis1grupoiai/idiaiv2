from django.urls import path
from. import views

urlpatterns = [
    path('facial/', views.inicio, name='inicio'),
    path('video/', views.video, name='video'),
    # path('webcam/', views.webcam, name='webcam'),

]