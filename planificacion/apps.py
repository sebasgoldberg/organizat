#encoding=utf-8
from django.apps import AppConfig

class PlanificacionConfig(AppConfig):
    name = 'planificacion'
    verbose_name = u"Planificación"

    def ready(self, *args, **kwargs):
        
        from .signals import *
