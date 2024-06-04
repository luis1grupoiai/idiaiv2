from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'imprimir_hola_mundo': {
        'task': 'apps.ActiveDirectory.tasks.imprimir_hola_mundo',  # Reemplaza con la ruta de tu función
        'schedule': timedelta(hours=24),  # Ejecutar una vez al día
        'args': (),
    },
}