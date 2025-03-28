from django.core.management.base import BaseCommand
from apps.areas.models import Gerencia
from django.contrib.auth.models import User
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Copia los registros de las gerencias, omitiendo las que ya existen'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT idGerencia, idDireccion, nombre, nombreCorto, encargado, abreviatura, borrado FROM [bdidiai].[dbo].[vAreas] WHERE idDepartamento IS NULL AND idGerencia IS NOT NULL
            """)
            registros_origen = cursor.fetchall()  # Guardar los registros antes de cerrar el cursor

        # Contadores para estadísticas
        total = len(registros_origen)
        creados = 0
        existentes = 0
        errores = 0

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET IDENTITY_INSERT areas_gerencia ON;")

            try:
                for registro in registros_origen:
                    idGerencia, idDireccion, nombre, nombreCorto, encargado, abreviatura, borrado = registro
                    try:
                        # Verificar si la gerencia ya existe
                        if Gerencia.objects.using('default').filter(id=idGerencia).exists():
                            existentes += 1
                            self.stdout.write(self.style.WARNING(
                                f'Gerencia con ID {idGerencia} ya existe. Omitiendo.'
                            ))
                            continue

                        # Intentar obtener el usuario
                        try:
                            usuario = User.objects.using('default').get(username=encargado)
                            id_gerente = usuario.id
                        except User.DoesNotExist:
                            self.stdout.write(self.style.WARNING(
                                f'Usuario {encargado} no existe. Se asignará NULL en id_gerente para la Gerencia {idGerencia}.'
                            ))
                            id_gerente = None  # Asignar None en lugar de omitir el registro

                        estado = 1 if borrado == 0 else 0

                        # Crear el nuevo registro de Gerencia
                        nuevo_registro = Gerencia(
                            id=idGerencia,
                            nombre=nombre,
                            abreviatura= abreviatura,
                            id_direccion_id=idDireccion, 
                            id_gerente_id=id_gerente,  # Asignar None si no existe usuario
                            estado=estado,
                        )
                        nuevo_registro.save(using='default')
                        creados += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'Gerencia {idGerencia} creada exitosamente.'
                        ))

                    except Exception as e:
                        errores += 1
                        self.stdout.write(self.style.ERROR(
                            f'Error al procesar registro {idGerencia}: {str(e)}'
                        ))

            finally:
                with connection.cursor() as cursor:
                    cursor.execute("SET IDENTITY_INSERT areas_gerencia OFF;")

        # Resumen final
        self.stdout.write(self.style.SUCCESS('\nResumen del proceso:'))
        self.stdout.write(f'• Total de registros procesados: {total}')
        self.stdout.write(f'• Gerencias creadas: {creados}')
        self.stdout.write(f'• Gerencias existentes (omitidas): {existentes}')
        self.stdout.write(f'• Registros con errores: {errores}')
