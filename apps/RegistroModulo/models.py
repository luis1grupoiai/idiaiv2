from django.db import models
from cryptography.fernet import Fernet



ENCRYPTION_KEY_DESCRIPCION = b'VVsQPaM9IhXYrWNwLyKkAnmJdzdFR8R0MwdvZpHGsA8='
ENCRYPTION_KEY_NOMBRE = b'o2GwoZ4O2UyRvsWTK7owoZKHOBQU2TbmYHUkHI1OWMs='

class TRegistroDeModulo(models.Model):
    _nombre = models.TextField()
    _descripcion = models.TextField()  # Usamos TextField para soportar datos encriptados más grandes
    nombre_completo = models.TextField()  # Nuevo campo agregado
    
    @property
    def nombre(self):
        n = Fernet(ENCRYPTION_KEY_NOMBRE)
       
        try:
            return n.decrypt(self._nombre.encode()).decode()
        except:
            return ""

    @nombre.setter
    def nombre(self, value):
        n = Fernet(ENCRYPTION_KEY_NOMBRE)
        
        self._nombre = n.encrypt(value.encode()).decode()

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












