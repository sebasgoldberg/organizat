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

class ParticionarItemsPedidoTestCase(TestCase):

    def validar_particion_producto(self, pedido, producto, cant_producto,
            cant_producto_por_item):
        """
        Valida que el pedido se haya particionado correctamente 
        respecto del producto indicado, donde se respete la cantidad
        de producto cant_producto y que si se tienen N items para el producto
        indicado, al menos N-1 contencan cant_producto_por_item.
        """

        cant_items_con_cantidad_exacta_esperados = cant_producto / cant_producto_por_item


        cant_producto_restante = cant_producto % cant_producto_por_item
        if cant_producto_restante > 0:
            cant_items_con_cant_restante_esperados = 1
        else:
            cant_items_con_cant_restante_esperados = 0

        cant_items_con_cantidad_exacta = 0
        cant_items_con_cant_restante = 0

        # Al tener un item con 100 unidades, si queremos tener 15 unidades por item,
        # la idea es que nos queden 100/15 items de 15 unidades y 
        # 1 item de 100 % 15 unidades
        for item in pedido.get_items_producto(producto):
          if item.cantidad == cant_producto_por_item:
            cant_items_con_cantidad_exacta += 1
          elif item.cantidad == cant_producto_restante:
            cant_items_con_cant_restante += 1
          else:
            self.fail("La cantidad %s para el item %s es incorrecta." % (
              item.cantidad, item))

        self.assertEqual(cant_items_con_cantidad_exacta,
                cant_items_con_cantidad_exacta_esperados)

        self.assertEqual(cant_items_con_cant_restante,
                cant_items_con_cant_restante_esperados)

        self.assertEqual(cant_items_con_cantidad_exacta*cant_producto_por_item + 
                cant_items_con_cant_restante*cant_producto_restante,
                cant_producto)

    def test_particionar_un_item(self):

        prodx = Producto.objects.create()
        
        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(prodx,100)

        pedido.particionar(producto=prodx,cantidad_por_item=15)

        self.validar_particion_producto(pedido, prodx, 100, 15)


    def test_particionar_un_item_exacto(self):

        prodx = Producto.objects.create()
        
        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(prodx,100)

        pedido.particionar(producto=prodx,cantidad_por_item=10)

        self.validar_particion_producto(pedido, prodx, 100, 10)


    def test_particionar_dos_items_mismo_producto(self):

        prodx = Producto.objects.create()
        
        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(prodx,100)
        pedido.add_item(prodx,100)

        pedido.particionar(producto=prodx,cantidad_por_item=15)

        self.validar_particion_producto(pedido, prodx, 200, 15)

    def test_particionar_dos_items_dos_producto(self):

        prodx = Producto.objects.create()
        prody = Producto.objects.create()
        
        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(prodx,100)
        pedido.add_item(prody,100)

        pedido.particionar(producto=prodx,cantidad_por_item=15)
        pedido.particionar(producto=prody,cantidad_por_item=9)

        self.validar_particion_producto(pedido, prodx, 100, 15)
        self.validar_particion_producto(pedido, prody, 100, 9)

    def test_particionar_multiples_items_dos_producto(self):

        prodx = Producto.objects.create()
        prody = Producto.objects.create()
        
        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(prodx,100)
        pedido.add_item(prodx,100)
        pedido.add_item(prody,100)
        pedido.add_item(prody,100)
        pedido.add_item(prody,100)

        pedido.particionar(producto=prodx,cantidad_por_item=15)
        pedido.particionar(producto=prody,cantidad_por_item=9)

        self.validar_particion_producto(pedido, prodx, 200, 15)
        self.validar_particion_producto(pedido, prody, 300, 9)

    def test_no_particionar_si_ya_particionado(self):

        prodx = Producto.objects.create()
        prody = Producto.objects.create()
        
        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(prodx,100)
        pedido.add_item(prodx,100)
        pedido.add_item(prody,100)
        pedido.add_item(prody,100)
        pedido.add_item(prody,100)

        pedido.particionar(producto=prodx,cantidad_por_item=15)
        pedido.particionar(producto=prody,cantidad_por_item=9)

        self.assertRaises(PedidoYaParticionado, pedido.particionar,producto=prodx, cantidad_por_item=15)
        self.assertRaises(PedidoYaParticionado, pedido.particionar,producto=prody, cantidad_por_item=9)

    def test_reparticionar(self):

        prodx = Producto.objects.create()
        prody = Producto.objects.create()
        
        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(prodx,100)
        pedido.add_item(prodx,100)
        pedido.add_item(prody,100)
        pedido.add_item(prody,100)
        pedido.add_item(prody,100)

        pedido.particionar(producto=prodx,cantidad_por_item=15)
        pedido.particionar(producto=prody,cantidad_por_item=9)

        pedido.particionar(producto=prodx,cantidad_por_item=14)
        pedido.particionar(producto=prody,cantidad_por_item=5)

        self.validar_particion_producto(pedido, prodx, 200, 14)
        self.validar_particion_producto(pedido, prody, 300, 5)


class ParticionadoDependiendoDeEstadoTestCase(TestCase):

    def test_particionar_productos_no_planificados(self):

        producto = Producto.objects.create()
        tarea = Tarea.objects.create(tiempo=4)
        maquina = Maquina.objects.create()

        maquina.add_tarea(tarea)
        producto.add_tarea(tarea)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,100)

        pedido.planificar()

        self.assertRaises(
                ProductoConPlanificacionExistente,
                pedido.particionar,
                producto=producto, cantidad_por_item=12)

