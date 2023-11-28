# Relacion 1 a 1

# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class Coordinacion(models.Model):
#     nombre = models.CharField(max_length=255)

#     def __str__(self):
#         return self.nombre

# class User(AbstractUser):
#     # Agrega tus campos personalizados aquí
#     coordinacion = models.ForeignKey(Coordinacion, on_delete=models.SET_NULL, null=True, blank=True)

#     def __str__(self):
#         return 'Nombre: ' + self.first_name + ' ' + self.last_name + ' - Coordinación: ' + self.coordinacion.nombre

# Opcion 2

# from django.contrib.auth.models import User
# from django.db import models

# class UserCoordinacion(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     coordinacion = models.ForeignKey('mycore.Coordinacion', on_delete=models.SET_NULL, null=True, blank=True)

#     def __str__(self):
#         return 'Nombre: ' + self.user.first_name + ' ' + self.user.last_name + ' - Coordinación: ' + self.coordinacion.nombre
#     class Meta:
#         # Personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
#         verbose_name = 'Coordinación de usuarios'
#         verbose_name_plural = 'Coordinación de usuarios'

# class Coordinacion(models.Model):
#     nombre = models.CharField(max_length=255)
#     abreviatura = models.CharField(max_length=10)
#     id_coordinador = models.ForeignKey(User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    

#     def __str__(self):
#         return self.nombre
#     class Meta:
#         # Personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
#         verbose_name = 'Coordinación'
#         verbose_name_plural = 'Coordinación'

# opcion 3


