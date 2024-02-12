from django.urls import path, re_path
from .views import  CapiArchivos
# from .views import swagger_json

# from django.urls import re_path
from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views
from rest_framework.response import Response
from rest_framework.views import APIView 
from rest_framework.permissions import IsAuthenticated

from drf_yasg.views import get_schema_view
from drf_yasg import openapi



urlpatterns = [
    # path('video/', views.video, name='video'),
    # path('webcam/', views.webcam, name='webcam'),
   #path('auth/', CAutenticacion.as_view(), name='auth'),
   #path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
   #path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
   #path('protegida/', Protegida.as_view(), name='protegida'),
   path('Docprueba/', CapiArchivos.as_view(), name='Docprueba'),
  #  path('Docprueba/', CCompareFacess.as_view(), name='Docprueba'),
  # path('documentos/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
  # path('verifytk/', CVerificaToken.as_view(), name='verifytk'),

]
