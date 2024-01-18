from django.db import models
from cryptography.fernet import Fernet

ENCRYPTION_KEY = b'VVsQPaM9IhXYrWNwLyKkAnmJdzdFR8R0MwdvZpHGsA8='

class TRegistroDeModulo(models.Model):
    nombre = models.CharField(max_length=128)
    _descripcion = models.CharField(max_length=1024)  

    @property
    def descripcion(self):
        f = Fernet(ENCRYPTION_KEY)
        try:
            return f.decrypt(self._descripcion.encode()).decode()
        except:
            return ""

    @descripcion.setter
    def descripcion(self, value):
        f = Fernet(ENCRYPTION_KEY)
        self._descripcion = f.encrypt(value.encode()).decode()  

    def __str__(self):
        return self.nombre

    class Meta:
        managed = False
        db_table = 'TRegistroDeModulo'