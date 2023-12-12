from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('mycore/', include('apps.mycore.urls')),
    path('api/', include('apps.rfacial.urls')),   
    path('areas/', include('apps.areas.urls')),
    path('AD/', include('apps.ActiveDirectory.urls'),name='ActDir'),
    path('', include('apps.ActiveDirectory.urls'),name='index'),
    path('accounts/', include ('django.contrib.auth.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

