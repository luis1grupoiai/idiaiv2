from django.db import models
from cryptography.fernet import Fernet



ENCRYPTION_KEY_DESCRIPCION = b'VVsQPaM9IhXYrWNwLyKkAnmJdzdFR8R0MwdvZpHGsA8='
ENCRYPTION_KEY_NOMBRE = b'VVsQPaM9IhXYrWNwLyKkAnmJdzdFR8R0MwdvZpHGsA8='

class TRegistroDeModulo(models.Model):
    _nombre = models.TextField()
    _descripcion = models.TextField()  # Usamos TextField para soportar datos encriptados más grandes

    @property
    def nombre(self):
        f = Fernet(ENCRYPTION_KEY_NOMBRE)
        try:
            return f.decrypt(self._nombre.encode()).decode()
        except:
            return ""

    @nombre.setter
    def nombre(self, value):
        f = Fernet(ENCRYPTION_KEY_NOMBRE)
        self._nombre = f.encrypt(value.encode()).decode()

    @property
    def descripcion(self):
        f = Fernet(ENCRYPTION_KEY_DESCRIPCION)
        try:
            return f.decrypt(self._descripcion.encode()).decode()
        except:
            return ""

    @descripcion.setter
    def descripcion(self, value):
        f = Fernet(ENCRYPTION_KEY_DESCRIPCION)
        self._descripcion = f.encrypt(value.encode()).decode()

    def __str__(self):
        return self.nombre

    class Meta:
        managed = False
        db_table = 'TRegistroDeModulo'











