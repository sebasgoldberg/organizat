# coding=utf-8
from .base import *

class StandsTestCase(PlanificadorTestCase):

    def test_planificacion(self):

        """
        Se define calendario lu a vi de 8 a 12 y de 13 a 17.
        """
        calendario = CalendarioProduccion.get_instance()

        calendario.add_intervalos_laborables(
          dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES,
            DiaSemana.MIERCOLES,DiaSemana.JUEVES,DiaSemana.VIERNES],
          hora_desde=T(8), hora_hasta=T(12))

        calendario.add_intervalos_laborables(
          dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES,
            DiaSemana.MIERCOLES,DiaSemana.JUEVES,DiaSemana.VIERNES],
          hora_desde=T(13), hora_hasta=T(17))

        """
        Se define el, producto, las tareas que lo componene y los recursos
        a utilizar.
        """
        producto = Producto.objects.create(descripcion='Stand')

        tarea_armado = Tarea.objects.create(
            descripcion='Armado', tiempo=18)
        tarea_embalaje = Tarea.objects.create(
            descripcion='Embalaje', tiempo=9)
        tarea_grafica_cenefas = Tarea.objects.create(
            descripcion='Grafica Cenefas', tiempo=12)
        tarea_pintura = Tarea.objects.create(
            descripcion='Pintura', tiempo=24)
        tarea_termoformado = Tarea.objects.create(
            descripcion='Termoformado', tiempo=30)

        maquina_mano_obra = Maquina.objects.create(descripcion='Mano de Obra')
        maquina_plotter = Maquina.objects.create(descripcion='Plotter')
        maquina_cabina_pintura = Maquina.objects.create(descripcion='Cabina Pintura')
        maquina_termoformadora_1 = Maquina.objects.create(descripcion='Termoformadora 1')
        maquina_termoformadora_2 = Maquina.objects.create(descripcion='Termoformadora 2')

        """
        Se indica qué recurso realiza qué tarea(s).
        """
        maquina_mano_obra.add_tarea(tarea_armado)
        maquina_mano_obra.add_tarea(tarea_embalaje)
        maquina_plotter.add_tarea(tarea_grafica_cenefas)
        maquina_cabina_pintura.add_tarea(tarea_pintura)
        maquina_termoformadora_1.add_tarea(tarea_termoformado)
        maquina_termoformadora_2.add_tarea(tarea_termoformado)

        """
        Se indica de que tareas se compone el producto a realizar.
        """
        producto.add_tarea(tarea_armado)
        producto.add_tarea(tarea_embalaje)
        producto.add_tarea(tarea_grafica_cenefas)
        producto.add_tarea(tarea_pintura)
        producto.add_tarea(tarea_termoformado)

        """
        Se define el flujo de trabajo a través de las dependencias:
        termoformado ---> grafica_cenefas --> armado ---> embalaje
                     ---> pintura         -->
        """
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_grafica_cenefas, tarea=tarea_armado)
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_pintura, tarea=tarea_armado)
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_armado, tarea=tarea_embalaje)
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_termoformado, tarea=tarea_grafica_cenefas)
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_termoformado, tarea=tarea_pintura)

        """
        Se crea un pedido de 50 unidades del producto, se asocia un cronograma
        a dicho pedido y se realiza la planificación del mismo a partir del
        4 de diciembre del 2014 a las 8 de la mañana.
        """
        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,50)
        cronograma = pedido.crear_cronograma(fecha_inicio=
                TZ.make_aware(DT(2014,12,4,8),
                    TZ.get_default_timezone()),
                _particionar_pedidos=False)
        cronograma.planificar()

        """
        Se verifica que se haya planificado correctamente las cantidades de 
        tarea en función de la cantidad de unidades de producto a producir.
        """
        self.verificar_cantidad_planificada(cronograma)

        """
        Se verifica que los intervalos planificados se encuentren dentro
        del calendario definido.
        """
        self.verificar_calendario(cronograma)

        """
        Se verifica que se respeten las dependencias entre las tareas.
        Básicamente la cantidad de tarea dependiente no puede superar
        en cantidad a la tarea de la cual depende.
        """
        self.verificar_dependencias(cronograma)
