from django.contrib.auth.models import User
from django.db import models
from apps.AsignarUsuario.models import VallEmpleado
from django.core.exceptions import ValidationError

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
    
    def clean(self):
        """Validación de la jerarquía organizacional"""
        super().clean()
        
        # Un usuario no puede tener coordinación y gerencia asignadas directamente
        if self.coordinacion and self.gerencia:
            raise ValidationError(
                "Un usuario no puede tener coordinación y gerencia asignadas directamente. "
                "La gerencia se deriva de la coordinación."
            )
            
        # Si tiene coordinación, heredar automáticamente su gerencia y dirección
        if self.coordinacion and not self.gerencia:
            self.gerencia = self.coordinacion.id_gerencia
        
        # Si tiene gerencia, heredar automáticamente su dirección
        if self.gerencia and not self.direccion:
            self.direccion = self.gerencia.id_direccion
        
        # Si tiene coordinación pero no dirección, heredar de la coordinación
        if self.coordinacion and not self.direccion:
            self.direccion = self.coordinacion.id_direccion

    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecuta las validaciones
        super().save(*args, **kwargs)
    
    @property
    def nivel_asignacion(self):
        """Devuelve el nivel organizacional más específico asignado"""
        if self.coordinacion:
            return 'Coordinación'
        if self.gerencia:
            return 'Gerencia'
        if self.direccion:
            return 'Dirección'
        return 'Sin asignación específica'
    
    @property
    def jerarquia_completa(self):
        """Devuelve la jerarquía completa del usuario"""
        return {
            'direccion': self.direccion,
            'gerencia': self.gerencia,
            'coordinacion': self.coordinacion
        }

    class Meta:
        verbose_name = 'Asignación de área'
        verbose_name_plural = 'Asignaciones de áreas'
        db_table = 'areas_userareas'
        managed = False