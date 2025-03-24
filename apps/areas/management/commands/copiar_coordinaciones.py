from django.core.management.base import BaseCommand
from apps.areas.models import Gerencia, Coordinacion
from apps.AsignarUsuario.models import VallEmpleado
from django.contrib.auth.models import User
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Copia los registros de las coordinaciones, omitiendo las que ya existen por nombre'

    def handle(self, *args, **kwargs):
        # Filtrar registros con "COORDINADOR" en Nombre_ct
        registros_origen = VallEmpleado.objects.using('default').filter(
            Nombre_ct__icontains='COORDINADOR',
            EstadoEmpleado='Contratado'  # Solo empleados contratados
        ).exclude(id_dir__isnull=True)  # Excluir registros sin dirección

        # Contadores para estadísticas
        total = registros_origen.count()
        creados = 0
        existentes = 0
        errores = 0

        with transaction.atomic():
            try:
                for registro in registros_origen:
                    try:
                        # Normalizar el nombre para comparación
                        nombre_modificado = registro.Nombre_ct.replace("COORDINADOR", "COORDINACIÓN ").strip()
                        
                        # Verificar si la coordinación ya existe por nombre
                        if Coordinacion.objects.using('default').filter(nombre__iexact=nombre_modificado).exists():
                            existentes += 1
                            self.stdout.write(self.style.NOTICE(
                                f'Coordinación "{nombre_modificado}" ya existe. Omitiendo.'
                            ))
                            continue

                        # Obtener usuario y validar
                        usuario = User.objects.using('default').get(username=registro.username)
                        
                        # Crear nueva coordinación
                        nueva_coordinacion = Coordinacion(
                            nombre=nombre_modificado,
                            id_direccion_id=registro.id_dir, 
                            id_coordinador_id=usuario.id,
                            estado=1,
                        )
                        nueva_coordinacion.save(using='default')
                        creados += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'Coordinación "{nombre_modificado}" (ID: {nueva_coordinacion.id}) creada exitosamente.'
                        ))

                    except User.DoesNotExist:
                        errores += 1
                        self.stdout.write(self.style.WARNING(
                            f'Usuario {registro.username} no existe. Coordinación "{nombre_modificado}" no creada.'
                        ))
                    except Exception as e:
                        errores += 1
                        self.stdout.write(self.style.ERROR(
                            f'Error al procesar registro {registro.id}: {str(e)}'
                        ))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error inesperado: {str(e)}'))
                raise

        # Resumen final mejorado
        self.stdout.write(self.style.SUCCESS('\nResumen del proceso:'))
        self.stdout.write(self.style.SUCCESS(f'• Total de registros procesados: {total}'))
        self.stdout.write(self.style.SUCCESS(f'• Coordinaciones creadas: {creados}'))
        self.stdout.write(self.style.WARNING(f'• Coordinaciones existentes (omitidas): {existentes}'))
        self.stdout.write(self.style.ERROR(f'• Registros con errores: {errores}'))