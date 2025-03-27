from django.core.management.base import BaseCommand
from apps.areas.models import Direccion, VDirecciones
from django.contrib.auth.models import User
from django.db import connection

class Command(BaseCommand):
    help = 'Copia los registros de la tabla vDirecciones a Direccion'

    def handle(self, *args, **kwargs):
        # Obtener los registros de la tabla origen (vDirecciones)
        registros_origen = VDirecciones.objects.using('idiaiv1').all()

        # Activar IDENTITY_INSERT para la tabla Direccion
        with connection.cursor() as cursor:
            cursor.execute("SET IDENTITY_INSERT areas_direccion ON;")

        try:
            # Recorrer los registros y copiarlos a la tabla destino (Direccion)
            for registro in registros_origen:
                try:
                    # Verificar si el registro ya existe en Direccion
                    if Direccion.objects.using('default').filter(id=registro.idDireccion).exists():
                        self.stdout.write(self.style.WARNING(
                            f'El registro con id {registro.idDireccion} ya existe en Direccion. Omitiendo.'
                        ))
                        continue

                    # Obtener el usuario correspondiente al encargado en vDirecciones
                    usuario = User.objects.using('default').get(username=registro.encargado)

                    # Convertir el campo borrado (0/1) a estado (1/0)
                    estado = 1 if registro.borrado == 0 else 0
                    
                    # Crear un nuevo registro en la tabla destino
                    nuevo_registro = Direccion(
                        id=registro.idDireccion,  # Asignar idDireccion a id
                        nombre=registro.nombre,
                        nombreCorto=registro.nombreCorto,
                        abreviatura=registro.abreviatura,
                        rfc=registro.rfc,
                        id_director_id=usuario.id,
                        estado=estado,
                    )
                    # Guardar el nuevo registro en la base de datos default
                    nuevo_registro.save(using='default')
                    self.stdout.write(self.style.SUCCESS(
                        f'Registro {registro.idDireccion} copiado exitosamente.'
                    ))

                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f'El usuario con username {registro.encargado} no existe en auth_user. Registro {registro.idDireccion} ignorado.'
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error al procesar el registro {registro.idDireccion}: {str(e)}'
                    ))
        finally:
            # Desactivar IDENTITY_INSERT para la tabla Direccion
            with connection.cursor() as cursor:
                cursor.execute("SET IDENTITY_INSERT areas_direccion OFF;")

        self.stdout.write(self.style.SUCCESS('Proceso de copia finalizado.'))