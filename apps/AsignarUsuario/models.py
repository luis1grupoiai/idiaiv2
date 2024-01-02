from django.db import models



        
class VallEmpleado(models.Model):
    id = models.IntegerField(primary_key=True)
    id_personal = models.IntegerField(unique=True)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    Nombre_ps = models.CharField(max_length=150)
    Apaterno_ps = models.CharField(max_length=150)
    Amaterno_ps = models.CharField(max_length=150)
    is_superuser = models.BooleanField()
    NombreCompleto = models.CharField(max_length=300)
    email = models.EmailField(max_length=254)
    date_joined = models.DateTimeField()
    RutaFoto_ps = models.CharField(max_length=200)
    Nombre_ct = models.CharField(max_length=200)
    nombre_direccion = models.CharField(max_length=200)
    nombre_coordinacion = models.CharField(max_length=200)
    

    class Meta:
        managed = False
        db_table = 'vAllEmpleados'