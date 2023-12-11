from django.contrib.auth.models import AbstractUser, User
from django.db import models

class UserCoordinacion(models.Model):
    # Campo de clave única que establece una relación uno a uno con el modelo de usuario predeterminado de Django (User)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Campo de clave externa que establece una relación muchos a uno con el modelo Coordinacion del módulo areas
    # Si la Coordinacion asociada se elimina, el campo coordinacion se establecerá en NULL
    coordinacion = models.ForeignKey('areas.Coordinacion', on_delete=models.SET_NULL, null=True, blank=True)

    # Método para obtener una representación de cadena del objeto UserCoordinacion
    def __str__(self):
        # Devuelve el nombre del usuario y el nombre de la coordinación (o 'Sin coordinación' si no hay coordinación)
        return 'Nombre: ' + self.user.first_name + ' ' + self.user.last_name + ' - Coordinación: ' + (self.coordinacion.nombre if self.coordinacion else 'Sin coordinación')
    
    # Clase Meta que personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
    class Meta:
        verbose_name = 'Coordinación de usuarios'
        verbose_name_plural = 'Coordinación de usuarios'

class Direccion(models.Model):
    nombre = models.CharField(max_length=255)
    abreviatura = models.CharField(max_length=10)
    rfc = models.CharField(max_length=30)
    id_director = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.nombre
        # Personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
        verbose_name = 'Direcciones'
        verbose_name_plural = 'Direcciones'

class Gerencia(models.Model):
    nombre = models.CharField(max_length=255)
    abreviatura = models.CharField(max_length=10)
    id_gerente = models.ForeignKey(User, on_delete=models.CASCADE)
    id_direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.nombre
        # Personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
        verbose_name = 'Gerencias'
        verbose_name_plural = 'Gerencias'

class Coordinacion(models.Model):
    nombre = models.CharField(max_length=255)
    abreviatura = models.CharField(max_length=10)
    id_coordinador = models.ForeignKey(User, on_delete=models.CASCADE)
    id_gerencia = models.ForeignKey(Gerencia, on_delete=models.CASCADE,  null=True, blank=True, default=None)
    id_direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.nombre
        # Personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
        verbose_name = 'Coordinaciones'
        verbose_name_plural = 'Coordinaciones'



