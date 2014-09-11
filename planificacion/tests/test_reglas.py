# coding=utf-8

from django.test import TestCase
from produccion.models import Producto, Maquina, Tarea
from planificacion.models import PedidoPlanificable
from planificacion.reglas import ItemYaPlanificado

class ReglasItemPedidoTestCase(TestCase):

    def test_item_ya_planificado(self):

        producto1 = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=10)
        maquina = Maquina.objects.create()

        maquina.add_tarea(tarea1)
        producto1.add_tarea(tarea1)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto1,10)

        cronograma = pedido.crear_cronograma()

        item = pedido.itempedido_set.first()

        item.cantidad = 12
        item.save()
        
        cronograma.planificar()

        item.cantidad = 15
        self.assertRaises(ItemYaPlanificado, item.clean)

        cronograma.activar()

        item.cantidad = 15
        self.assertRaises(ItemYaPlanificado, item.clean)

        cronograma.finalizar()

        item.cantidad = 15
        self.assertRaises(ItemYaPlanificado, item.clean)

    def test_item_no_planificado(self):

        producto1 = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=10)
        maquina = Maquina.objects.create()

        maquina.add_tarea(tarea1)
        producto1.add_tarea(tarea1)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto1,10)

        cronograma = pedido.crear_cronograma()

        item = pedido.itempedido_set.first()

        cronograma.planificar()
        cronograma.invalidar()

        item.cantidad = 12
        item.save()

        cronograma.planificar()
        cronograma.activar()
        cronograma.intervalocronograma_set.first().cancelar()

        item.cantidad = 15
        item.save()
