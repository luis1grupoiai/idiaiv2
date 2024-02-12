from django.db import models

class datab(models.Model):
    
    STATUS_CHOICES = [
         ('Activo', 'Activo'),
         ('Inactivo', 'Inactivo'),
     ]
    
    nombre = models.CharField(max_length=10)
    descripcion  = models.CharField(max_length=150)
    estatus = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'BD'
        
class Disk(models.Model):
    
    STATUS_CHOICES = [
         ('Activo', 'Activo'),
         ('Inactivo', 'Inactivo'),
     ]
    
    nombre = models.CharField(max_length=10)
    descripcion  = models.CharField(max_length=150)
    url  = models.CharField(max_length=150)
    estatus = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Disk'

class Modelos(models.Model):
    
    STATUS_CHOICES = [
         ('Activo', 'Activo'),
         ('Inactivo', 'Inactivo'),
     ]
    
    nombre = models.CharField(max_length=10)
    descripcion  = models.CharField(max_length=150)
    estatus = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Modelos'

class Archivo(models.Model): 
    
    STATUS_CHOICES = [
         ('Activo', 'Activo'),
         ('Inactivo', 'Inactivo'),
     ]
     
    nombre = models.CharField(max_length=255)
    id_bd = models.ManyToManyField(datab)
    id_modelo = models.ManyToManyField(Modelos)
    id_disk =  models.ManyToManyField(Disk)
    tipo_archivo = models.CharField(max_length=150)
    extension =  models.CharField(max_length=150)   
    ruta = models.CharField(max_length=150)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Activo')
    version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'Archivos'
