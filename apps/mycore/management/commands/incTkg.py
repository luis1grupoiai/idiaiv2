from django.core.management.base import BaseCommand
from apps.rfacial.views.views import CInactivaTkg

class Command(BaseCommand):
    help = 'Este es un comando personalizado de Django'

    def handle(self, *args, **options):
        # Aquí va tu lógica
        oInc = CInactivaTkg()

        oInc.inactivarRegistrosTkg()

        # self.stdout.write('¡Hola desde mi script de Django!')
