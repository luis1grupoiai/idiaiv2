from django.apps import AppConfig


class SistemasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sistemas'
    def ready(self):
        import apps.sistemas.signals