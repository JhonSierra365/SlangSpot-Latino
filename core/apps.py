from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Se ejecuta cuando la aplicación está lista.
        Conecta las señales personalizadas.
        """
        import core.signals  # noqa
