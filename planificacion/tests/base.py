# coding=utf-8
from django.test import TestCase
from produccion.models import * 
from planificacion.models import * 
from calendario.models import DiaSemana
import datetime
import pytz
from django.db.transaction import rollback
from django.utils.translation import ugettext as _
from datetime import time as T
from datetime import datetime as DT
from decimal import Decimal as D
from calendario.models import *
from django.conf import settings
import os

utc=pytz.UTC

FIXTURE_TEST_DIR = os.path.join(settings.BASE_DIR, 'planificacion', 'fixtures', 'tests')

def getFixture(fixtureFileName):
    return os.path.join(FIXTURE_TEST_DIR,fixtureFileName)

class PlanificadorTestCase(TestCase):

  def verificar_cantidad_planificada(self, cronograma):

    # Se verifica que se haya planificado la cantidad 
    # que corresponde de cada tarea.
    for pedido in cronograma.get_pedidos():
      for item in pedido.get_items():
        for tarea in item.producto.get_tareas():
          cantidad_tarea = cronograma.intervalocronograma_set.filter(
            tarea=tarea,item=item).aggregate(
            models.Sum('cantidad_tarea'))['cantidad_tarea__sum']
          self.assertLessEqual(abs(item.cantidad - cantidad_tarea),
            cronograma.get_tolerancia(item.cantidad), 
            'Intervalos involucrados: %s' % cronograma.intervalocronograma_set.filter(
              tarea=tarea,item=item))

