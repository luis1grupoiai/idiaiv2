from django.urls import path, re_path
from .views import CAutenticacion
# from .views import swagger_json

# from django.urls import re_path
from rest_framework import permissions
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
                  "url": "http://127.0.0.1:8000/api/auth/",
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
   path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   #  path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
   #  re_path(r'^swagger(?P<format>\.json)$', swagger_json, name='swagger-json'),
   # path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   # re_path(r'^swagger(?P<format>\.json)$', swagger_json, name='swagger-json'),
]