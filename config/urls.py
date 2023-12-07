from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mycore/', include('apps.mycore.urls')),
    path('api/', include('apps.rfacial.urls')),   
    path('componentes/', include('apps.componentes.urls')),   
    path('areas/', include('apps.areas.urls')),
    path('AD/', include('apps.ActiveDirectory.urls'),name='ActDir'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

