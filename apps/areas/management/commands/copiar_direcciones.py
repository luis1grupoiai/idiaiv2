from django.core.management.base import BaseCommand
from apps.areas.models import Direccion, VDirecciones
from django.contrib.auth.models import User
from django.db import connection

class Command(BaseCommand):
    help = 'Copia los registros de la tabla vDirecciones a Direccion'

    def handle(self, *args, **kwargs):
        # Obtener los registros de la tabla origen (vDirecciones)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT idDireccion, nombre, nombreCorto, abreviatura, rfc, encargado, borrado
                FROM [bdidiai].[dbo].[vAreas]
                WHERE idDepartamento IS NULL AND idGerencia IS NULL AND idDireccion IS NOT NULL
            """)
            registros_origen = cursor.fetchall()  # Guardar antes de que el cursor se cierre

        # Activar IDENTITY_INSERT para la tabla Direccion
        with connection.cursor() as cursor:
            cursor.execute("SET IDENTITY_INSERT areas_direccion ON;")

        try:
            # Recorrer los registros y copiarlos a la tabla destino (Direccion)
            for registro in registros_origen:
                id_direccion, nombre, nombre_corto, abreviatura, rfc, encargado, borrado = registro

                # Verificar si el registro ya existe en Direccion
                if Direccion.objects.using('default').filter(id=id_direccion).exists():
                    self.stdout.write(self.style.WARNING(
                        f'El registro con id {id_direccion} ya existe en Direccion. Omitiendo.'
                    ))
                    continue

                # Obtener el usuario correspondiente al encargado en vDirecciones
                try:
                    usuario = User.objects.using('default').get(username=encargado)
                    id_director = usuario.id
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f'El usuario con username {encargado} no existe en auth_user. Se asignará NULL en id_director para el registro {id_direccion}.'
                    ))
                    id_director = None  # Asignar None en lugar de omitir el registro

                # Convertir el campo borrado (0/1) a estado (1/0)
                estado = 1 if borrado == 0 else 0
                
                # Crear un nuevo registro en la tabla destino
                nuevo_registro = Direccion(
                    id=id_direccion,
                    nombre=nombre,
                    nombreCorto=nombre_corto,
                    abreviatura=abreviatura,
                    rfc=rfc,
                    id_director_id=id_director,
                    estado=estado,
                )
                # Guardar el nuevo registro en la base de datos default
                nuevo_registro.save(using='default')
                self.stdout.write(self.style.SUCCESS(
                    f'Registro {id_direccion} copiado exitosamente.'
                ))

        finally:
            # Desactivar IDENTITY_INSERT para la tabla Direccion
            with connection.cursor() as cursor:
                cursor.execute("SET IDENTITY_INSERT areas_direccion OFF;")

        self.stdout.write(self.style.SUCCESS('Proceso de copia finalizado.'))
