from django.core.management.base import BaseCommand
from apps.rfacial.views.views import CMigraPermisos

class Command(BaseCommand):
    help = 'El siguiente comando sirve para apoyo a la migración de los permisos de IDIAI v1 a IDIAI v2; tambien puede ser utilizado para asignar permisos de forma masiva a todos los usuarios de un sistema en especifico o asignar un permiso a un usuario en un sistema en especifico. '

    def add_arguments(self, parser):
        parser.add_argument('arg1', type=str, help='Nombre en mayusculas del sistema a consultar.')

        parser.add_argument(
            '--arg2',
            type=str,
            help='Nombre del usuario/Allkn/Alluk(en construcción); Donde si el parametro es Allkn realiza una busqueda para obtener solo los usuarios que ya cuentan con permisos al sistema descrito en arg1 y a estos mismos asignarle el permiso de arg3;Alluk realiza una busqueda absoluta de todos los usuarios para asignarle el permiso escrito en arg3, sin importar que los usuarios cuenten o no con permisos al sistema de arg1; si el parametro es el nombre de un usuario entonces solo a ese usuario se le asignara el o los permisos descritos en arg3. Este parametro es opcional.',
            default=None
        )

        parser.add_argument(
            '--arg3',
            type=str,
            help='Listado de permisos que se desean asignar al usuario, el listado debe estar separado por comas ó si solo se pasa un permiso entonces no debe llevar comas. Este parametro es opcional.',
            default=None
        )


        parser.add_argument(
            '--arg4',
            type=str,
            help='Nombre de permiso al que se va correlacionar el permiso indicado en el arg3.',
            default=None
        )

    def handle(self, *args, **options):
        # Aquí va tu lógica
        sSistema = ""
        sUsuarios = ""
        sPermisos = ""
        bValido = True

        arg1 = options['arg1']
        arg2 = options.get('arg2',"")
        arg3 = options.get('arg3',"")
        arg4 = options.get('arg4',"")

        self.stdout.write(f'Se obtendran los usuarios que tienen acceso al sistema : {arg1}')
        self.stdout.write(f'Argumento 2 : {arg2}')
        self.stdout.write(f'Argumento 3 : {arg3}')
        self.stdout.write(f'Argumento 4 : {arg4}')

        sSistema = f'{arg1}'
        sSistema =  sSistema.upper().strip()

        sUsuarios = arg2
        sPermisos = arg3
        sPermisoIdiaiv1 = arg4


        if sUsuarios == None:
            print("No se ingreso usuarios en arg2.")
        else:
            if sPermisos == None:
                bValido = False
                print("No hay permisos en arg3.")
                print("Debe ingresar datos tanto en Arg2 como en Arg3 para que funcione la asignación de permisos especificos a todos o a ciertos usuarios.")

        if sPermisos == None:
                print("No hay permisos en arg3.")
        else:
            if sUsuarios == None:
                bValido = False
                print("No hay usuarios en arg2.")
                print("Debe ingresar datos tanto en Arg2 como en Arg3 para que funcione la asignación de permisos especificos a todos o a ciertos usuarios.")

        if sSistema!="" and bValido:
            oInc = CMigraPermisos()
            oInc.migrarPermisos(sSistema,sUsuarios, sPermisos,sPermisoIdiaiv1)
        else:
            print("No ingreso correctamento los argumentos, por favor de verificar el uso del comando consultado  migrarPermisos --help")

        # self.stdout.write('¡Hola desde mi script de Django!')
