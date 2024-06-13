from django.core.management.base import BaseCommand
from apps.rfacial.views.views import CMigraPermisos

class Command(BaseCommand):
    help = 'El siguiente comando sirve para apoyo a la migración de los permisos de IDIAI v1 a IDIAI v2.'

    def add_arguments(self, parser):
        parser.add_argument('arg1', type=str, help='Nombre en mayusculas del sistema a consultar.')

    def handle(self, *args, **options):
        # Aquí va tu lógica
        sSistema = ""

        arg1 = options['arg1']
        self.stdout.write(f'Se obtendran los usuarios que tienen acceso al sistema : {arg1}')

        sSistema = f'{arg1}'
        sSistema =  sSistema.upper().strip()


        if sSistema!="":
            oInc = CMigraPermisos()
            oInc.migrarPermisos(sSistema)
        else:
            print("No ingreso ningun sistema, por favor ingrese el nombre de algun sistema.")

        # self.stdout.write('¡Hola desde mi script de Django!')
