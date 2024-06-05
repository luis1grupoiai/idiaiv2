from celery import shared_task

@shared_task
def imprimir_hola_mundo():
    """
    Tarea Celery para imprimir el mensaje "Hola Mundo".
    """
    print("Hola Mundo!")