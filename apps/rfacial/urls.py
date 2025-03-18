from django.urls import path, re_path
from .views import CAutenticacion
from .views import Protegida
from .views import CVerificaToken
from .views import CVerificaTokenGlobal
from .views import CVerificarTokenPermiso
# from .views import swagger_json

# from django.urls import re_path
from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .views import CAutenticacion, CReconFacial, CCompareFaces
from .views.views import CPhotoView, EnviarCorreoAPIView

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="API Auth",
      default_version='v 1.0.0',
      description="Api de autenticación de ID IAI",
      contact=openapi.Contact(email="ana.sanchez@grupo-iai.com.mx"),
      license=openapi.License(name="BSD License"),
      servers=[
               {
                  "url": "http://127.0.0.1:8000/api/",
                  "description": "Servidor de desarrollo para api de autenticación.",
               },
            ]
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   
)


urlpatterns = [
    # path('facial/', views.inicio, name='inicio'),
    # path('video/', views.video, name='video'),
    # path('webcam/', views.webcam, name='webcam'),
   path('auth/', CAutenticacion.as_view(), name='auth'),
   path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
   path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
   path('protegida/', Protegida.as_view(), name='protegida'),
   path('ReconFacial/', CReconFacial.as_view(), name='ReconFacial'),
   path('CompareFaces/', CCompareFaces.as_view(), name='CompareFaces'),
   path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('verifytk/', CVerificaToken.as_view(), name='verifytk'),
   path('verifytkG/', CVerificaTokenGlobal.as_view(), name='verifytkG'),
   path('photo_view/', CPhotoView.as_view(), name='photo_view'),
   path('enviarCorreo/', EnviarCorreoAPIView.as_view(), name='enviarCorreo'),
   path('verifyTkper/', CVerificarTokenPermiso.as_view(), name='verifyTkper'),

   
   #  path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
   #  re_path(r'^swagger(?P<format>\.json)$', swagger_json, name='swagger-json'),
   # path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   # re_path(r'^swagger(?P<format>\.json)$', swagger_json, name='swagger-json'),
]
