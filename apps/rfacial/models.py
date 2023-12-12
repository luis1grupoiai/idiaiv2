from django.db import models

# Create your models here.

class vUsuarioPermiso(models.Model):

    class Meta:
        managed = False
        db_table = 'vUsuarioPermiso'
    
    def __str__(self):
        return self.username
