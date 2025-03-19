from django.db import models

# Create your models here.

class vUsuarioPermiso(models.Model):

    class Meta:
        managed = False
        db_table = 'vUsuarioPermiso'
    
    def __str__(self):
        return self.username

class RasgosFaciales(models.Model):
    id = models.IntegerField(primary_key=True)
    #ide_personal = models.ForeignKey('AsignarUsuario.VallEmpleado', on_delete=models.SET_NULL, null=True, to_field='id_personal')
    id_personal = models.CharField(max_length=200)
    rasgos_faciales = models.JSONField()

class TokenGlobal(models.Model):

    # Campo de opciones limitadas para el estado del sistema (Activo o Inactivo)
    STATUS_CHOICES = [
         ('1', '1'),
         ('0', '0'),
     ]
    
    username = models.CharField(max_length=50)
    sistemaOrigen = models.IntegerField()
    token = models.TextField()
    caduco = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)    


class intentos(models.Model):

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    numintentos = models.IntegerField()
    idSistema = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fechaCadReg = models.DateTimeField()
    activo = models.IntegerField()
    observaciones = models.TextField(max_length=100)
    token = models.CharField(max_length=250) #ARSI 19/03/2025 SE AGREGA CAMPO TOKEN
    tokenActivo = models.IntegerField()  #ARSI 19/03/2025 SE AGREGA CAMPO TOKEN ACTIVO

    class Meta:
        managed = False
        db_table = 'THistorialAccesos'

    


    

    
