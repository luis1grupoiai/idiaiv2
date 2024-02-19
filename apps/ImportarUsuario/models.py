from django.db import models

# Create your models here.
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