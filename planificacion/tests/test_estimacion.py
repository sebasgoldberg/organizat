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

class EstimarDuracionProduccionProductoTestCase(TestCase):

    #@profile
    def test_estimar_producto_una_maquina(self):

        producto = Producto.objects.create()
        tarea = Tarea.objects.create(tiempo=60)
        maquina = Maquina.objects.create()

        maquina.add_tarea(tarea)
        producto.add_tarea(tarea)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,100)

        cronograma = pedido.crear_cronograma()

        self.assertEqual(
                cronograma.estimar_tiempo_fabricacion_producto(producto),
                60*60)

        self.assertEqual(Cronograma.objects.count(),1)
        self.assertEqual(MaquinaCronograma.objects.count(),1)
        self.assertEqual(PedidoCronograma.objects.count(),1)
        self.assertEqual(IntervaloCronograma.objects.count(),0)
        self.assertEqual(Pedido.objects.count(),1)
        self.assertEqual(ItemPedido.objects.count(),1)

    #@profile
    def test_estimar_producto_dos_maquinas(self):

        producto = Producto.objects.create()
        tarea = Tarea.objects.create(tiempo=60)
        maquina1 = Maquina.objects.create(descripcion='M1')
        maquina2 = Maquina.objects.create(descripcion='M2')

        maquina1.add_tarea(tarea)
        maquina2.add_tarea(tarea)
        producto.add_tarea(tarea)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,100)

        cronograma = pedido.crear_cronograma()

        self.assertEqual(
                cronograma.estimar_tiempo_fabricacion_producto(producto),
                30*60)

    #@profile
    def test_estimar_producto_dos_tareas(self):

        producto = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=60)
        tarea2 = Tarea.objects.create(descripcion='T2', tiempo=30)
        maquina = Maquina.objects.create(descripcion='M1')

        maquina.add_tarea(tarea1)
        maquina.add_tarea(tarea2)
        producto.add_tarea(tarea1)
        producto.add_tarea(tarea2)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,100)

        cronograma = pedido.crear_cronograma()

        self.assertLess(
                abs(cronograma.estimar_tiempo_fabricacion_producto(producto)-
                    90*60),
                cronograma.get_tolerancia(90*60))


    #@profile
    def test_estimar_producto_tareas_dependientes(self):

        producto = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=60)
        tarea2 = Tarea.objects.create(descripcion='T2', tiempo=30)
        maquina1 = Maquina.objects.create(descripcion='M1')
        maquina2 = Maquina.objects.create(descripcion='M2')

        maquina1.add_tarea(tarea1)
        maquina2.add_tarea(tarea2)

        producto.add_tarea(tarea1)
        producto.add_tarea(tarea2)

        producto.add_dependencia_tareas(tarea_anterior=tarea1, tarea=tarea2)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,100)

        cronograma = pedido.crear_cronograma()

        tiempo_esperado = 60*60

        self.assertLess(
                abs(cronograma.estimar_tiempo_fabricacion_producto(producto)-
                    tiempo_esperado),
                cronograma.get_tolerancia(tiempo_esperado))



    #@profile
    def test_estimar_producto_3_tareas_dependientes(self):

        producto = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=60)
        tarea2 = Tarea.objects.create(descripcion='T2', tiempo=30)
        tarea3 = Tarea.objects.create(descripcion='T3', tiempo=80)
        maquina1 = Maquina.objects.create(descripcion='M1')
        maquina3 = Maquina.objects.create(descripcion='M3')

        maquina1.add_tarea(tarea1)
        maquina1.add_tarea(tarea2)
        maquina3.add_tarea(tarea3)

        producto.add_tarea(tarea1)
        producto.add_tarea(tarea2)
        producto.add_tarea(tarea3)

        producto.add_dependencia_tareas(tarea_anterior=tarea1, tarea=tarea2)
        producto.add_dependencia_tareas(tarea_anterior=tarea2, tarea=tarea3)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,100)

        cronograma = pedido.crear_cronograma()

        tiempo_esperado = 140*60

        self.assertLess(
                abs(cronograma.estimar_tiempo_fabricacion_producto(producto)-
                    tiempo_esperado),
                cronograma.get_tolerancia(tiempo_esperado))


    #@profile
    def test_estimar_producto_con_calendario(self):

        calendario = CalendarioProduccion.get_instance()

        # se define calendario lu a vi de 8 a 8:30
        calendario.add_intervalos_laborables(
          dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES,
            DiaSemana.MIERCOLES,DiaSemana.JUEVES,DiaSemana.VIERNES],
          hora_desde=T(8), hora_hasta=T(8,30))

        producto = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=60)
        tarea2 = Tarea.objects.create(descripcion='T2', tiempo=30)
        tarea3 = Tarea.objects.create(descripcion='T3', tiempo=80)
        maquina1 = Maquina.objects.create(descripcion='M1')
        maquina3 = Maquina.objects.create(descripcion='M3')

        maquina1.add_tarea(tarea1)
        maquina1.add_tarea(tarea2)
        maquina3.add_tarea(tarea3)

        producto.add_tarea(tarea1)
        producto.add_tarea(tarea2)
        producto.add_tarea(tarea3)

        producto.add_dependencia_tareas(tarea_anterior=tarea1, tarea=tarea2)
        producto.add_dependencia_tareas(tarea_anterior=tarea2, tarea=tarea3)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,100)

        cronograma = pedido.crear_cronograma()

        tiempo_esperado = 140*60

        self.assertLess(
                abs(cronograma.estimar_tiempo_fabricacion_producto(producto)-
                    tiempo_esperado),
                cronograma.get_tolerancia(tiempo_esperado))

