# coding=utf-8
from django.db import models
from cleansignal.models import CleanSignal
from django.utils.translation import ugettext_lazy as _
from planificacion.models import IntervaloCronograma, Cronograma
from produccion.models import Maquina

class CostoBaseModel(CleanSignal, models.Model):
  class Meta:
    abstract = True


class CostoModel(CostoBaseModel):
  costo = models.DecimalField(
    max_digits=12, decimal_places=3, verbose_name=_(u'Costo ($)'),
    editable=False, default=0)
  class Meta:
    abstract = True


class CostoMaquina(CostoBaseModel):
  maquina = models.ForeignKey(Maquina, verbose_name=_(u'Maquina'), editable=False)
  costo_por_hora = models.DecimalField(default=0,
    max_digits=12, decimal_places=3, verbose_name=_(u'Costo ($/h)'), 
    help_text=_(u'Costo de utilización de la máquina por hora.'))


class CostoIntervalo(CostoModel):

  intervalo = models.ForeignKey(IntervaloCronograma, verbose_name=_(u'Intervalo'),
      editable=False, unique=True)


class CostoCronograma(CostoModel):

  cronograma = models.ForeignKey(Cronograma, verbose_name=_(u'Cronograma'),
      editable=False, unique=True)


import costos.signals
