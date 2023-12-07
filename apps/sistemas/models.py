from django.db import models
from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist


# Create your models here.
class Sistemas(models.Model):
    nombre = models.CharField(max_length=255)
    STATUS_CHOICES = [
         ('Activo', 'Activo'),
         ('Inactivo', 'Inactivo'),
     ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Activo')
    version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
        # Personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
        verbose_name = 'Sistemas'
        verbose_name_plural = 'Sistemas'


class SistemaPermiso(models.Model):
    sistema = models.OneToOneField(Sistemas, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        # Personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
        verbose_name = 'Permisos Sistemas'
        verbose_name_plural = 'Permisos Sistemas'
        unique_together = ('sistema', 'permiso')

    def __str__(self):
        try:
            permiso_nombre = self.permiso.name
        except ObjectDoesNotExist:
            permiso_nombre = 'Permiso no encontrado'

        return f'{self.sistema} - {permiso_nombre}'  

    