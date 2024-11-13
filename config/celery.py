from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Configura el entorno de Django usando settings.development como predeterminado
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Crea una instancia de Celery con el nombre del proyecto
app = Celery('django-project')

# Carga la configuración desde settings.py, ajustando el namespace a CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Busca automáticamente tareas en las aplicaciones del proyecto
app.autodiscover_tasks()

