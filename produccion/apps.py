#encoding=utf8
from django.apps import AppConfig

class ProduccionConfig(AppConfig):
    name = 'produccion'
    verbose_name = "Producción"

    def ready(self, *args, **kwargs):
        
        from .signals import *
