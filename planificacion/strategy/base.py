# coding=utf-8
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

class PlanificadorStrategy:

  cronograma = None

  def __init__(self, cronograma):
    self.cronograma = cronograma
  
  def planificar(self):
    raise Exception(_(u'Método no implementado'))

