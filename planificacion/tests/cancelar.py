# coding=utf-8
from .base import *
from planificacion.signals import *


class CancelarTestCase(TestCase):

    #@profile
    def test_cancelacion_parcial_replanificacion(self):
        """
        La idea de esta prueba es:
        - Planificar un cronograma.
        - Verificar que los intervalos de dicho cronograma no pueden ser cancelados.
        - Activar el cronograma.
        - Ordenar los intervalos por dependencia.
        - Cancelar algún intervalo intermedio.
        - Verificar que se cumplan las condiciones de intervalo cancelado.
        - Verificar que los intervalos dependientes fueron cancelados.
        - Se planifica la parte cancelada del pedido en otro cronograma.
        - Se verifica que la cantidad planificada por tarea del nuevo cronograma
            coincida con las cantidades de los intervalos cancelados.
        """

        producto = Producto.objects.create(descripcion='P1')
        tarea1 = Tarea.objects.create(descripcion='T1', tiempo=30)
        tarea2 = Tarea.objects.create(descripcion='T2', tiempo=40)
        tarea3 = Tarea.objects.create(descripcion='T3', tiempo=50)
        tarea4 = Tarea.objects.create(descripcion='T4', tiempo=60)
        maquina1 = Maquina.objects.create(descripcion='M1')
        maquina2 = Maquina.objects.create(descripcion='M2')

        maquina1.add_tarea(tarea1)
        maquina1.add_tarea(tarea2)
        maquina2.add_tarea(tarea3)
        maquina2.add_tarea(tarea4)

        producto.add_tarea(tarea1)
        producto.add_tarea(tarea2)
        producto.add_tarea(tarea3)
        producto.add_tarea(tarea4)

        producto.add_dependencia_tareas(tarea_anterior=tarea1, tarea=tarea2)
        producto.add_dependencia_tareas(tarea_anterior=tarea2, tarea=tarea3)
        producto.add_dependencia_tareas(tarea_anterior=tarea3, tarea=tarea4)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,5)

        cronograma = pedido.crear_cronograma()

        cronograma.planificar()

        #- Verificar que los intervalos de dicho cronograma no pueden ser cancelados.
        for intervalo in cronograma.get_intervalos_ordenados_por_dependencia():
            # No se debería poder cancelar un intervalo que no esté activo
            self.assertRaises(EstadoIntervaloCronogramaError,intervalo.cancelar)
            break

        #- Activar el cronograma.
        cronograma.activar()

        #- Ordenar los intervalos por dependencia.
        intervalos = []
        for intervalo in cronograma.get_intervalos_ordenados_por_dependencia():
            intervalos.append(intervalo)

        #- Cancelar algún intervalo intermedio.
        # Se obtiene un intervalo con grado intermedio
        indice_intermedio = len(intervalos) / 2
        intervalo_cancelado = intervalos[indice_intermedio]

        # Se asigna 10 a la cantidad de tarea real.
        intervalo_cancelado.cantidad_tarea_real = 10
        intervalo_cancelado.clean()
        intervalo_cancelado.save()

        intervalo_cancelado.cancelar()

        #- Verificar que se cumplan las condiciones de intervalo cancelado.
        # Luego de cancelar el intervalo se verifica que esté cancelado
        # y que la cantidad de tarea real sea nula
        self.assertTrue(intervalo_cancelado.is_cancelado())
        self.assertEqual(intervalo_cancelado.cantidad_tarea_real, 0)

        intervalo_cancelado.cantidad_tarea_real = 2
        # No se puede modificar un intervalo cancelado
        self.assertRaises(EstadoIntervaloCronogramaError, intervalo_cancelado.clean)

        #- Verificar que los intervalos dependientes fueron cancelados.
        # Se verifica que los intervalos subsiguientes hayan sido cancelados.
        for intervalo_dependiente in intervalo_cancelado.get_intervalos_dependientes():
          self.assertTrue(intervalo_dependiente.is_cancelado())


        #- Se planifica la parte cancelada del pedido en otro cronograma.
        cronograma2 = pedido.crear_cronograma()
        cronograma2.planificar()


        #- Se verifica que la cantidad planificada por tarea del nuevo cronograma
        #    coincida con las cantidades de los intervalos cancelados.

        # Se verifica que coincidan los intervalos planificados del pedido de
        # neumáticos de autos con los intervalos cancelados.
        cantidadTarea={}

        for intervaloCancelado in IntervaloCronograma.objects.filter(
            cronograma=cronograma,
            estado=ESTADO_INTERVALO_CANCELADO): 
            cantidadTarea.setdefault(intervaloCancelado.tarea.id,0)
            cantidadTarea[intervaloCancelado.tarea.id]+=intervaloCancelado.cantidad_tarea;

        for intervaloPlanificado in IntervaloCronograma.objects.filter(
            cronograma=cronograma2,
            item__in=[i for i in pedido.get_items()]):
            cantidadTarea[intervaloPlanificado.tarea.id]-=intervaloPlanificado.cantidad_tarea;

        for cantidad in cantidadTarea.itervalues():
            self.assertEqual(cantidad, 0)
            


