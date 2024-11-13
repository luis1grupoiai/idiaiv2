from celery import shared_task
import time

# @shared_task
# def tarea_larga():
#     # Simula una tarea que toma tiempo
#     time.sleep(10)
#     return "La tarea en segundo plano se ha completado."  # Asegúrate de retornar un valor

@shared_task
def sumar(a, b):
    return a + b