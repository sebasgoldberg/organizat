#encoding=utf8
from django.apps import AppConfig

class PlanificacionConfig(AppConfig):
    name = 'planificacion'
    verbose_name = "Planificación"

    def ready(self, *args, **kwargs):
        
        from .signals import *
