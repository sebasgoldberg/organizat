# coding=utf-8
from .base import *

class CantidadExtraTareaAnteriorTestCase(TestCase):

    #@profile
    def test_cantidad_extra_tarea_anterior(self):

        producto = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=30)
        tarea2 = Tarea.objects.create(descripcion='T2', tiempo=30)
        maquina1 = Maquina.objects.create(descripcion='M1')
        maquina2 = Maquina.objects.create(descripcion='M2')

        maquina1.add_tarea(tarea1)
        maquina2.add_tarea(tarea2)

        tp1 = producto.add_tarea(tarea1)
        tp2 = producto.add_tarea(tarea2)

        producto.add_dependencia_tareas(tarea_anterior=tarea1, tarea=tarea2)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,100)

        cronograma = pedido.crear_cronograma(
            cantidad_extra_tarea_anterior=2,
            tiempo_minimo_intervalo=0)

        cronograma.planificar()

        fecha_fin_tarea1 = tp1.intervalocronograma_set.aggregate(
            Max('fecha_hasta'))['fecha_hasta__max']
        fecha_fin_tarea2 = tp2.intervalocronograma_set.aggregate(
            Max('fecha_hasta'))['fecha_hasta__max']

        defasaje = (fecha_fin_tarea2 -
            fecha_fin_tarea1).total_seconds()

        self.assertLess(
                abs(defasaje-3600),
                cronograma.get_tolerancia(3600))


    #@profile
    def test_sin_cantidad_extra_tarea_anterior(self):

        producto = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=30)
        tarea2 = Tarea.objects.create(descripcion='T2', tiempo=30)
        maquina1 = Maquina.objects.create(descripcion='M1')
        maquina2 = Maquina.objects.create(descripcion='M2')

        maquina1.add_tarea(tarea1)
        maquina2.add_tarea(tarea2)

        tp1 = producto.add_tarea(tarea1)
        tp2 = producto.add_tarea(tarea2)

        producto.add_dependencia_tareas(tarea_anterior=tarea1, tarea=tarea2)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,100)

        cronograma = pedido.crear_cronograma(
            cantidad_extra_tarea_anterior=0)

        cronograma.planificar()

        fecha_fin_tarea1 = tp1.intervalocronograma_set.aggregate(
            Max('fecha_hasta'))['fecha_hasta__max']
        fecha_fin_tarea2 = tp2.intervalocronograma_set.aggregate(
            Max('fecha_hasta'))['fecha_hasta__max']

        defasaje = (fecha_fin_tarea2 -
            fecha_fin_tarea1).total_seconds()

        self.assertEqual(defasaje,0)


