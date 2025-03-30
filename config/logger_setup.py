import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class LoggerSetup:
    def __init__(self, app_name, name=__name__, level=logging.DEBUG):
        # Determinar si estamos en producción o desarrollo
        env = os.environ.get('DJANGO_ENV', 'development')
        if env == 'production':
            log_file = f'{app_name}_prod'
        else:
            log_file = f'{app_name}_dev'

        # Obtener la ruta absoluta del directorio de logs en el directorio base
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', app_name)
        os.makedirs(log_dir, exist_ok=True)

        # Obtener la fecha actual
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Formatear log_file_path para incluir la fecha en el formato requerido
        log_file_path_with_date = os.path.join(log_dir, f"{log_file}_{current_date}.log")

        # Usar un nombre de logger único por aplicación y entorno
        logger_name = f"{name}.{app_name}.{env}"
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)

        # Evitar añadir múltiples handlers si ya existen
        if not any(isinstance(handler, TimedRotatingFileHandler) for handler in self.logger.handlers):
            # Crear un TimedRotatingFileHandler directamente con el archivo que incluye la fecha
            file_handler = TimedRotatingFileHandler(
                log_file_path_with_date, when="midnight", interval=1, backupCount=30
            )
            file_handler.suffix = "%Y-%m-%d"
            file_handler.extMatch = r"^\d{4}-\d{2}-\d{2}$"  # Ajustar la expresión regular para el sufijo

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Desactivar la propagación
        self.logger.propagate = False

    def get_logger(self):
        return self.logger

    @staticmethod
    def setup_logger_for_environment(app_name, env=None):
        if env is None:
            env = os.environ.get('DJANGO_ENV', 'development')
        if env == 'production':
            return LoggerSetup(app_name, level=logging.INFO).get_logger()
        else:  # Default to development settings
            return LoggerSetup(app_name).get_logger()
