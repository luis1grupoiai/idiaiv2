from django.core.management.base import BaseCommand
from apps.ActiveDirectory.views import actualizar_empleados

class Command(BaseCommand):
    help = 'Este es un comando personalizado de Django'

    def handle(self, *args, **options):
        try:
            
            actualizar_empleados()           
            #self.stdout.write(self.style.SUCCESS('¡Hola desde mi script de Django!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
    