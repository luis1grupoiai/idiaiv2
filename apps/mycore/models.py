from django.db import models
from django.contrib.auth.models import Permission


class Permisos(Permission):
    # Agrega campos adicionales según tus necesidades
    descripcion = models.CharField(max_length=255)
    ACTIVO = '1'
    INACTIVO = '0'

    STATUS_CHOICES = [
        (ACTIVO, 'Activo'),
        (INACTIVO, 'Inactivo'),
    ]

    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=ACTIVO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)