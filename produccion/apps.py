#encoding=utf-8
from django.apps import AppConfig

class ProduccionConfig(AppConfig):
    name = 'produccion'
    verbose_name = u"Producción"

    def ready(self, *args, **kwargs):
        
        from .signals import *
