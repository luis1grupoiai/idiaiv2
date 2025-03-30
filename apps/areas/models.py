from django.contrib.auth.models import User
from django.db import models
from apps.AsignarUsuario.models import VallEmpleado
from django.core.exceptions import ValidationError

class ValidacionUsuarioUnico(models.Model):
    """Clase base para validar que un usuario no tenga múltiples roles activos."""

    class Meta:
        abstract = True  # No se creará una tabla para esta clase

    def validar_usuario(self, usuario, rol_actual, nombre): 
        """
        Verifica si un usuario ya ocupa otro rol activo en Dirección, Gerencia o Coordinación.
        :param usuario: Usuario a validar.
        :param rol_actual: Texto indicando el rol que se está asignando.
        """
        if usuario:
            errores = []

            # Verificar si ya es coordinador en otra coordinación activa
            if Coordinacion.objects.filter(id_coordinador=usuario, estado=1).exclude(id=self.id).exists():
                errores.append(f'El usuario {usuario.username} es coordinador en una Coordinación activa. Por lo tanto no puede ser {rol_actual} de {nombre}')

            # Verificar si ya es director en una dirección activa
            if Direccion.objects.filter(id_director=usuario, estado=1).exclude(id=self.id).exists():
                errores.append(f'El usuario {usuario.username} es director en una Dirección activa. Por lo tanto no puede ser {rol_actual} de {nombre}')

            # Verificar si ya es gerente en una gerencia activa
            if Gerencia.objects.filter(id_gerente=usuario, estado=1).exclude(id=self.id).exists():
                errores.append(f'El usuario {usuario.username} es gerente en una Gerencia activa. Por lo tanto no puede ser {rol_actual} de {nombre}')
            if errores:
                raise ValidationError(errores)

class Direccion(ValidacionUsuarioUnico):
    """Modelo de Dirección"""
    ESTADO_INACTIVO = 0
    ESTADO_ACTIVO = 1
    ESTADO_CHOICES = [(ESTADO_INACTIVO, 'Inactivo'), (ESTADO_ACTIVO, 'Activo')]

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

    def clean(self):
        """Valida que el usuario no tenga otro rol activo."""
        self.validar_usuario(self.id_director, "Director", self.nombre)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'


class Gerencia(ValidacionUsuarioUnico):
    """Modelo de Gerencia"""
    ESTADO_INACTIVO = 0
    ESTADO_ACTIVO = 1
    ESTADO_CHOICES = [(ESTADO_INACTIVO, 'Inactivo'), (ESTADO_ACTIVO, 'Activo')]

    nombre = models.CharField(max_length=255)
    abreviatura = models.CharField(max_length=10)
    id_gerente = models.ForeignKey(User, on_delete=models.CASCADE)
    id_direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estado = models.IntegerField(choices=ESTADO_CHOICES, default=ESTADO_ACTIVO)

    def __str__(self):
        return self.nombre

    def clean(self):
        """Valida que el usuario no tenga otro rol activo."""
        self.validar_usuario(self.id_gerente, "Gerente", self.nombre)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Gerencia'
        verbose_name_plural = 'Gerencias'


class Coordinacion(ValidacionUsuarioUnico):
    """Modelo de Coordinación"""
    ESTADO_INACTIVO = 0
    ESTADO_ACTIVO = 1
    ESTADO_CHOICES = [(ESTADO_INACTIVO, 'Inactivo'), (ESTADO_ACTIVO, 'Activo')]

    nombre = models.CharField(max_length=255)
    abreviatura = models.CharField(max_length=10, null=True)
    id_coordinador = models.ForeignKey(User, on_delete=models.CASCADE, db_constraint=False)
    id_gerencia = models.ForeignKey(Gerencia, on_delete=models.CASCADE, null=True, blank=True, default=None)
    id_direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estado = models.IntegerField(choices=ESTADO_CHOICES, default=ESTADO_ACTIVO)

    def __str__(self):
        return self.nombre

    def clean(self):
        """Valida que el usuario no tenga otro rol activo."""
        self.validar_usuario(self.id_coordinador, "Coordinador", self.nombre)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Coordinación'
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


class UserAreas(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id')
    coordinacion = models.ForeignKey(Coordinacion, on_delete=models.SET_NULL, 
                                   null=True, blank=True, db_column='coordinacion_id')
    gerencia = models.ForeignKey(Gerencia, on_delete=models.SET_NULL, 
                               null=True, blank=True, db_column='gerencia_id')
    direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, 
                                null=True, blank=True, db_column='direccion_id')

    def __str__(self):
        parts = [f'Usuario: {self.user.username}']
        if self.coordinacion:
            parts.append(f'Coordinación: {self.coordinacion.nombre}')
        if self.gerencia:
            parts.append(f'Gerencia: {self.gerencia.nombre}')
        if self.direccion:
            parts.append(f'Dirección: {self.direccion.nombre}')
        return ' - '.join(parts) if parts else 'Sin área asignada'
    
    class Meta:
        verbose_name = 'Asignación de área'
        verbose_name_plural = 'Asignaciones de áreas'
        db_table = 'areas_userareas'
        managed = False  # Indica que esta tabla ya existe en la base de datos
