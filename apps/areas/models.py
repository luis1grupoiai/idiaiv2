from django.contrib.auth.models import User
from django.db import models
from apps.AsignarUsuario.models import VallEmpleado

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
    
   
    class Meta:
        verbose_name = 'Coordinación de usuarios'
        verbose_name_plural = 'Coordinación de usuarios'


class Direccion(models.Model):
    ESTADO_INACTIVO = 0
    ESTADO_ACTIVO = 1
    ESTADO_CHOICES = [
        (ESTADO_INACTIVO, 'Inactivo'),
        (ESTADO_ACTIVO, 'Activo'),
    ]

    nombre = models.CharField(max_length=255)
    nombreCorto = models.CharField(max_length=100)
    abreviatura = models.CharField(max_length=10)
    rfc = models.CharField(max_length=30, null=True)
    id_director = models.ForeignKey(User, on_delete=models.CASCADE, db_constraint=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estado = models.IntegerField(choices=ESTADO_CHOICES, default=ESTADO_ACTIVO)
    
    def __str__(self):
        return self.nombre
        # Personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
        verbose_name = 'Direcciones'
        verbose_name_plural = 'Direcciones'


class Gerencia(models.Model):
    ESTADO_INACTIVO = 0
    ESTADO_ACTIVO = 1
    ESTADO_CHOICES = [
        (ESTADO_INACTIVO, 'Inactivo'),
        (ESTADO_ACTIVO, 'Activo'),
    ]
    nombre = models.CharField(max_length=255)
    abreviatura = models.CharField(max_length=10)
    id_gerente = models.ForeignKey(User, on_delete=models.CASCADE)
    id_direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estado = models.IntegerField(choices=ESTADO_CHOICES, default=ESTADO_ACTIVO)


    def __str__(self):
        return self.nombre
        # Personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
        verbose_name = 'Gerencias'
        verbose_name_plural = 'Gerencias'


class Coordinacion(models.Model):
    ESTADO_INACTIVO = 0
    ESTADO_ACTIVO = 1
    ESTADO_CHOICES = [
        (ESTADO_INACTIVO, 'Inactivo'),
        (ESTADO_ACTIVO, 'Activo'),
    ]
    nombre = models.CharField(max_length=255)
    abreviatura = models.CharField(max_length=10, null=True,)
    id_coordinador = models.ForeignKey(User, on_delete=models.CASCADE, db_constraint=False)
    id_gerencia = models.ForeignKey(Gerencia, on_delete=models.CASCADE,  null=True, blank=True, default=None)
    id_direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estado = models.IntegerField(choices=ESTADO_CHOICES, default=ESTADO_ACTIVO)

    
    def __str__(self):
        return self.nombre
        # Personaliza cómo se mostrará el nombre del modelo en la interfaz de administración de Django
        verbose_name = 'Coordinaciones'
        verbose_name_plural = 'Coordinaciones'


class VDirecciones(models.Model):
    idDireccion = models.IntegerField(primary_key=True)  # Clave primaria
    idGerencia = models.IntegerField()
    idCorporativo = models.IntegerField()
    idDepartamento = models.IntegerField()
    idArea = models.IntegerField()
    nombre = models.CharField(max_length=255)
    nombreCorto = models.CharField(max_length=100, null=True, blank=True)
    Id_personal = models.IntegerField(null=True, blank=True)
    encargado = models.CharField(max_length=255, null=True, blank=True)
    abreviatura = models.CharField(max_length=50, null=True, blank=True)
    rfc = models.CharField(max_length=13, null=True, blank=True)
    borrado = models.BooleanField(default=False)

    class Meta:
        db_table = 'vDirecciones'
        managed = False  # Indica que esta tabla ya existe en la base de datos

    def __str__(self):
        return self.nombre
