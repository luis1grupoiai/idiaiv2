from django.urls import path
from .views import CompanyView

urlpatterns = [
    # path('facial/', views.inicio, name='inicio'),
    # path('video/', views.video, name='video'),
    # path('webcam/', views.webcam, name='webcam'),
    path('companies/', CompanyView.as_view(), name='companies_list')
]