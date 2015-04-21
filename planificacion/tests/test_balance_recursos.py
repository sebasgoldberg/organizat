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

 
class BalanceRecursosTestCase(TestCase):

    #@profile
    def test_balance_recursos(self):

        producto1 = Producto.objects.create(descripcion='P1')
        producto2 = Producto.objects.create(descripcion='P2')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=6)
        tarea2 = Tarea.objects.create(descripcion='T2', tiempo=3)
        maquina1 = MaquinaPlanificacion.objects.create(descripcion='M1')
        maquina2 = MaquinaPlanificacion.objects.create(descripcion='M2')

        maquina1.add_tarea(tarea1)
        maquina1.add_tarea(tarea2)
        maquina2.add_tarea(tarea1)
        maquina2.add_tarea(tarea2)
        producto1.add_tarea(tarea1)
        producto2.add_tarea(tarea2)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto1,30)
        pedido.add_item(producto2,30)

        cronograma = pedido.crear_cronograma()

        cronograma.remove_maquina(maquina2)

        cronograma.planificar()

        cronograma.activar()

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto1,45)
        pedido.add_item(producto2,45)

        cronograma = pedido.crear_cronograma()

        cronograma.planificar()

        fecha_final_m1 = maquina1.get_intervalos().aggregate(
            models.Max('fecha_hasta'))['fecha_hasta__max']
        fecha_final_m2 = maquina2.get_intervalos().aggregate(
            models.Max('fecha_hasta'))['fecha_hasta__max']


        diferencia_entre_fechas_finales = fecha_final_m1-fecha_final_m2

        total_maquina2 = maquina2.get_intervalos(
            ).aggregate(total=models.Sum(
              'tiempo_intervalo'))['total'] * 60

        self.assertLessEqual(
            abs(diferencia_entre_fechas_finales.total_seconds()),
            cronograma.get_tolerancia(total_maquina2)
            )

