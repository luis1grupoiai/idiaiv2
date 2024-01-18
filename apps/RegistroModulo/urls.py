from django.urls import path
from .views import ModuloListView, ModuloCreateView, ModuloUpdateView, ModuloDeleteView , ver_detalle_registro  , bitacora

urlpatterns = [
    path('', ModuloListView.as_view(), name='modulo_list'),
    path('create/', ModuloCreateView.as_view(), name='modulo_create'),
    path('update/<int:pk>/', ModuloUpdateView.as_view(), name='modulo_update'),
    path('delete/<int:pk>/', ModuloDeleteView.as_view(), name='modulo_delete'),
    path('detalle/<int:id>/', ver_detalle_registro, name='detalle_registro'),
    path('bitacoraModulo/',  bitacora, name="bitacoraModulo" ),
]