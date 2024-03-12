from django.db import models

class TActiveDirectoryIp(models.Model):
    server = models.CharField(max_length=250)  # Asumiendo que 'server' es un campo de texto
    ip = models.CharField(max_length=250)  # Asumiendo que 'ip' es un campo de texto para almacenar una dirección IP

    class Meta:
        managed = False
        db_table = 'TActiveDirectoryIp'  # Especifica el nombre de la tabla si es diferente del nombre del modelo

    def __str__(self):
        return self.server
# Create your models here.
