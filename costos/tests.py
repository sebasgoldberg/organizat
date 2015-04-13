# coding=utf-8
from django.test import TestCase
from datetime import time as T
from datetime import datetime as DT
from django.utils.translation import ugettext as _
import datetime
from django.utils import timezone
from produccion.models import *
from planificacion.models import *
from .models import *

class CostosTestCase(TestCase):

  def test_crear_costo_maquina(self):

    maquina = Maquina.objects.create()

    self.assertTrue(CostoMaquina.objects.all().exists())

    costomaquina = CostoMaquina.objects.first()
    
    self.assertEqual(costomaquina.maquina.id, maquina.id)
    self.assertEqual(costomaquina.costo_por_hora, 0)


  def test_costo_intervalo(self):

    producto1 = Producto.objects.create(descripcion='P1')
    tarea1 = Tarea.objects.create(descripcion='T1', tiempo=6)
    maquina1 = MaquinaPlanificacion.objects.create(descripcion='M1')

    costomaq = maquina1.costomaquina_set.first()
    costomaq.costo_por_hora = 10
    costomaq.clean()
    costomaq.save()

    maquina1.add_tarea(tarea1)
    producto1.add_tarea(tarea1)

    pedido = PedidoPlanificable.objects.create()
    pedido.add_item(producto1,30)
    pedido.add_item(producto1,50)

    cronograma = pedido.crear_cronograma()

    cronograma.planificar()

    total = 0
    for intervalo in cronograma.get_intervalos():
      costointervalo = intervalo.costointervalo
      self.assertEqual(
          costointervalo.costo,
          (intervalo.get_duracion().total_seconds()/3600)*costomaq.costo_por_hora)
      total += costointervalo.costo

    self.assertEqual(total,
        cronograma.costocronograma.costo)

