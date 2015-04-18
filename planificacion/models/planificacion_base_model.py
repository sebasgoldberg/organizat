# coding=utf-8
from django.db import models
from cleansignal.models import CleanSignal

class PlanificacionBaseModel(CleanSignal):
  class Meta:
    abstract = True
    app_label = 'planificacion'


