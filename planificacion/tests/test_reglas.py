# coding=utf-8

from .base import *
from planificacion.reglas import (ItemYaPlanificado,
    IntervaloCalendarioConPlanificacionExistente,
    MaquinaYaUtilizadaEnPlanificacion,
    PedidoYaUtilizadoEnPlanificacion,
    ProductoYaUtilizadoEnPlanificacion)

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

        item.delete()

    def test_borrar_item_ya_planificado(self):

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

        self.assertRaises(ItemYaPlanificado, item.delete)


class ReglasExcepcionLaborableTestCase(TestCase):

    def test_agregar_excepcion_laborable(self):

        calendario = CalendarioProduccion.get_instance()

        # se define calendario lu y ma de 8 a 12
        calendario.add_intervalos_laborables(
          dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES, ],
          hora_desde=T(8), hora_hasta=T(12))

        producto1 = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=10)
        maquina = Maquina.objects.create()

        maquina.add_tarea(tarea1)
        producto1.add_tarea(tarea1)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto1,100)

        # Comienza un LUNES
        cronograma = pedido.crear_cronograma(
            fecha_inicio=utc.localize(DT(2014, 9, 8)))

        # Se deberían planificar:
        # LUNES 8/9/2014: 48 unidades
        # MARTES 9/9/2014: 48 unidades
        # LUNES 15/9/2014: 4 unidades
        cronograma.planificar()

        # Queremos agregar una excepción laborable un día que 
        # existe planificación.
        self.assertRaises(
            IntervaloCalendarioConPlanificacionExistente,
            calendario.add_excepcion_no_laborable,
            DT(2014,9,9),T(0),T(23))

        # Queremos agregar una excepción laborable en un horario
        # que existe planificación.
        self.assertRaises(
            IntervaloCalendarioConPlanificacionExistente,
            calendario.add_excepcion_no_laborable,
            DT(2014,9,9),T(9),T(10))

    def test_modificar_excepcion_laborable(self):

        calendario = CalendarioProduccion.get_instance()

        # se define calendario lu y ma de 8 a 12
        calendario.add_intervalos_laborables(
          dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES, ],
          hora_desde=T(8), hora_hasta=T(12))

        # Agregamos como excepción el miércoles 10/9
        excepcion = calendario.add_excepcion_laborable(
          datetime.date(2014,9,10),T(8),T(12))

        producto1 = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=10)
        maquina = Maquina.objects.create()

        maquina.add_tarea(tarea1)
        producto1.add_tarea(tarea1)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto1,100)

        # Comienza un LUNES
        cronograma = pedido.crear_cronograma(
            fecha_inicio=utc.localize(DT(2014, 9, 8)))

        # Se deberían planificar:
        # LUNES 8/9/2014: 48 unidades
        # MARTES 9/9/2014: 48 unidades
        # MIERCOLES 10/9/2014: 4 unidades
        cronograma.planificar()

        # Hacemos que la excepción del miércoles sea NO laborable
        excepcion.laborable = False
        self.assertRaises(
            IntervaloCalendarioConPlanificacionExistente,
            excepcion.clean)

        excepcion.laborable = True
        excepcion.clean()

        # Hacemos que la excepción del miércoles comience a las 9 hs,
        # en lugar de las 8 hs.
        excepcion.hora_desde = T(9)
        self.assertRaises(
            IntervaloCalendarioConPlanificacionExistente,
            excepcion.clean)

        self.assertRaises(
            IntervaloCalendarioConPlanificacionExistente,
            excepcion.delete)

    def test_modificar_excepcion_no_laborable(self):

        calendario = CalendarioProduccion.get_instance()

        # se define calendario lu y ma de 8 a 12
        calendario.add_intervalos_laborables(
          dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES, ],
          hora_desde=T(8), hora_hasta=T(12))

        # Agregamos como excepción el lunes 15/9
        excepcion = calendario.add_excepcion_laborable(
          datetime.date(2014,9,15),T(8),T(12))

        producto1 = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=10)
        maquina = Maquina.objects.create()

        maquina.add_tarea(tarea1)
        producto1.add_tarea(tarea1)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto1,100)

        # Comienza un LUNES
        cronograma = pedido.crear_cronograma(
            fecha_inicio=utc.localize(DT(2014, 9, 8)))

        # Se deberían planificar:
        # LUNES 8/9/2014: 48 unidades
        # MARTES 9/9/2014: 48 unidades
        # MARTES 16/9/2014: 4 unidades
        cronograma.planificar()

        # Hacemos que la excepción del lunes sea el martes.
        excepcion.fecha = datetime.date(2014, 9, 16)
        self.assertRaises(
            IntervaloCalendarioConPlanificacionExistente,
            excepcion.clean)
 
class ReglasMaquinaCronogramaTestCase(TestCase):

    def test_maquina_ya_utilizada(self):

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

        mc = cronograma.maquinacronograma_set.first()
        mc.maquina = MaquinaPlanificacion.objects.create(descripcion='M2')
        self.assertRaises(MaquinaYaUtilizadaEnPlanificacion,
            mc.clean)

        self.assertRaises(MaquinaYaUtilizadaEnPlanificacion,
          cronograma.remove_maquina, maquina)


class ReglasPedidoCronogramaTestCase(TestCase):

    def test_pedido_ya_utilizado(self):

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

        pc = cronograma.pedidocronograma_set.first()
        pc.pedido = PedidoPlanificable.objects.create(descripcion='P2')
        self.assertRaises(PedidoYaUtilizadoEnPlanificacion,
            pc.clean)

        self.assertRaises(PedidoYaUtilizadoEnPlanificacion,
          cronograma.remove_pedido, pedido)


class ReglasTareaProductoTestCase(TestCase):

    def test_pedido_ya_utilizado(self):

        producto1 = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=10)
        maquina = Maquina.objects.create()

        maquina.add_tarea(tarea1)
        tarea_producto = producto1.add_tarea(tarea1)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto1,10)

        cronograma = pedido.crear_cronograma()

        cronograma.planificar()

        tarea_producto.tarea = Tarea.objects.create(
            descripcion='T2', tiempo=11)

        self.assertRaises(ProductoYaUtilizadoEnPlanificacion,
            tarea_producto.clean)

        self.assertRaises(ProductoYaUtilizadoEnPlanificacion,
          tarea_producto.delete)

