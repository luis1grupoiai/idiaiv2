from django.db import models
from cryptography.fernet import Fernet

# Asumiendo que estas claves son importadas desde tu configuración o definidas en algún lugar seguro
ENCRYPTION_KEY_DESCRIPCION = b'VVsQPaM9IhXYrWNwLyKkAnmJdzdFR8R0MwdvZpHGsA8='
ENCRYPTION_KEY_NOMBRE = b'o2GwoZ4O2UyRvsWTK7owoZKHOBQU2TbmYHUkHI1OWMs='

class TRegistroDeModulo(models.Model):
    _nombre = models.TextField()
    _descripcion = models.TextField()

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
        managed = False  # Django no administrará la creación de la tabla para este modelo
        db_table = 'TRegistroDeModulo'  # Asegúrate de que este nombre coincida con el nombre de tu tabla en la base de datos
# Create your models here.
class VUsuariosModulo(models.Model):
    id = models.BigAutoField(primary_key=True)  # Asegura que corresponda al tipo de dato y llave primaria usada en la vista
    _nombre = models.CharField(max_length=255)  # Ajusta el max_length según tus necesidades
    _descripcion = models.TextField()  # Usamos TextField para descripciones que pueden ser largas

    class Meta:
        managed = False  # Django no creará, modificará, ni eliminará la tabla subyacente
        db_table = 'VUsuariosModulo'  # El nombre exacto de tu vista en SQL Server

    def __str__(self):
        return self._nombre
class VUsuarioDjango(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField()

    class Meta:
        managed = False  # No crear, modificar o eliminar tabla
        db_table = 'VUsuariosDjango'   # El nombre de tu vista en SQL Server
        
    """ esto es un regalo de mi yo del pasado para mi yo del futuro XD...
    CREATE VIEW VUsuariosDjango AS
        SELECT 
            ROW_NUMBER() OVER (ORDER BY usuario) AS id,
            pass2 AS password,
            NULL AS last_login,
            0 AS is_superuser,
            usuario AS username,
            nombre AS first_name,
            ISNULL(apellidoPaterno, '') + ' ' + ISNULL(apellidoMaterno, '') AS last_name,
            usuario + '@grupo-iai.com.mx' AS email,
            0 AS is_staff,
            status AS is_active,
            ISNULL(CONVERT(datetime, fechaRegistro, 120), GETDATE()) AS date_joined  -- Usar GETDATE() como alternativa
        FROM     
            bdidiai.dbo.USUARIOS;
    """