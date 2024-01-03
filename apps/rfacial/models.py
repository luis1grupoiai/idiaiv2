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


