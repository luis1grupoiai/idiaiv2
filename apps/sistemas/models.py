from django.db import models
from django.contrib.auth.models import Permission, Group, User
from django.core.exceptions import ObjectDoesNotExist

class Sistemas(models.Model):
    nombre = models.CharField(max_length=255)
    
    # Campo de opciones limitadas para el estado del sistema (Activo o Inactivo)
    STATUS_CHOICES = [
         ('Activo', 'Activo'),
         ('Inactivo', 'Inactivo'),
     ]
    # Campo de texto para almacenar el estado del sistema utilizando las opciones definidas en STATUS_CHOICES
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Activo')
    version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    visibleIntranet = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Activo')
    urlsistema = models.CharField(max_length=255, default='Sin definir')
    urlDoc = models.CharField(max_length=255, default='Sin definir')

    # Método para obtener una representación de cadena del objeto Sistemas (se devuelve el nombre del sistema)
    def __str__(self):
        return self.nombre

    # Clase Meta que personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
    class Meta:
        verbose_name = 'Sistemas'
        verbose_name_plural = 'Sistemas'


class SistemaPermisoGrupo(models.Model):
    # Campo de clave externa que establece una relación muchos a uno con el modelo Sistemas
    sistema = models.ForeignKey(Sistemas, on_delete=models.CASCADE)

    # Campo de clave externa que establece una relación muchos a uno con el modelo Permission (permisos de Django)
    # Si el permiso asociado se elimina, el campo permiso se establecerá en NULL
    permiso = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True, blank=True)

    # Campo de clave externa que establece una relación muchos a uno con el modelo Group (grupos de Django)
    # Si el grupo asociado se elimina, el campo grupo se establecerá en NULL
    grupo = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Clase Meta que personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
    # Además, establece una restricción única para que no haya duplicados de (sistema, permiso, grupo)
    class Meta:
        verbose_name = 'Sistemas Permisos Grupos'
        verbose_name_plural = 'Sistemas Permisos Grupos'
        unique_together = ('sistema', 'permiso', 'grupo')

    # Define el método __str__ para obtener una representación de cadena del objeto SistemaPermisoGrupo
    def __str__(self):
        # Define mensajes predeterminados en caso de que no se encuentre un permiso o grupo
        permiso_nombre = 'Permiso no encontrado'
        grupo_nombre = 'Grupo no encontrado'

        # Verifica si el objeto tiene un permiso asignado
        if self.permiso:
            # Si tiene un permiso, intenta obtener su nombre; si no tiene nombre, utiliza un mensaje predeterminado
            permiso_nombre = self.permiso.name if self.permiso.name else 'Permiso sin nombre'

        # Verifica si el objeto tiene un grupo asignado
        if self.grupo:
            # Si tiene un grupo, intenta obtener su nombre; si no tiene nombre, utiliza un mensaje predeterminado
            grupo_nombre = self.grupo.name if self.grupo.name else 'Grupo sin nombre'

        # Devuelve una cadena que incluye el nombre del sistema, el nombre del permiso y el nombre del grupo (o mensajes de error)
        return f'{self.sistema} - {permiso_nombre} - {grupo_nombre}'
    
class UserSPG(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spg = models.ForeignKey(SistemaPermisoGrupo, on_delete=models.CASCADE)


    