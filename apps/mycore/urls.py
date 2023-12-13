from django.urls import path
from. import views
from .views import CEjecutarSP

urlpatterns = [
    # path('', views.inicio, name='inicio'),
    path('ejecutarsp/', CEjecutarSP, name='execSP'),
]