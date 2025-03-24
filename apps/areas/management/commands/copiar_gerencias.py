from django.core.management.base import BaseCommand
from apps.areas.models import Gerencia
from apps.AsignarUsuario.models import VallEmpleado
from django.contrib.auth.models import User
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Copia los registros de las gerencias, omitiendo las que ya existen'

    def handle(self, *args, **kwargs):
        # Filtrar registros con "GERENTE" en Nombre_ct y que tengan idGerencia
        registros_origen = VallEmpleado.objects.using('default').filter(
            Nombre_ct__icontains='GERENTE',
            idGerencia__isnull=False
        )

        # Contadores para estadísticas
        total = registros_origen.count()
        creados = 0
        existentes = 0
        errores = 0

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET IDENTITY_INSERT areas_gerencia ON;")

            try:
                for registro in registros_origen:
                    try:
                        # Verificar si la gerencia ya existe
                        if Gerencia.objects.using('default').filter(id=registro.idGerencia).exists():
                            existentes += 1
                            self.stdout.write(self.style.WARNING(
                                f'Gerencia con ID {registro.idGerencia} ya existe. Omitiendo.'
                            ))
                            continue

                        usuario = User.objects.using('default').get(username=registro.username)
                        
                        if registro.EstadoEmpleado == 'Contratado':
                            # Modificar el nombre
                            nombre_modificado = registro.Nombre_ct.replace("GERENTE", "GERENCIA ")
                            
                            nuevo_registro = Gerencia(
                                id=registro.idGerencia,
                                nombre=nombre_modificado,
                                id_direccion_id=registro.id_dir, 
                                id_gerente_id=usuario.id,  
                                estado=1,
                            )
                            nuevo_registro.save(using='default')
                            creados += 1
                            self.stdout.write(self.style.SUCCESS(
                                f'Gerencia {registro.idGerencia} creada exitosamente.'
                            ))
                    except User.DoesNotExist:
                        errores += 1
                        self.stdout.write(self.style.WARNING(
                            f'Usuario {registro.username} no existe. Registro {registro.idGerencia} ignorado.'
                        ))
                    except Exception as e:
                        errores += 1
                        self.stdout.write(self.style.ERROR(
                            f'Error al procesar registro {registro.idGerencia}: {str(e)}'
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