# coding=utf-8
from .base import *

class NeumaticosTestCase(PlanificadorTestCase):

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
        producto = Producto.objects.create(descripcion='Neumático')

        _1_verificacion = Tarea.objects.create(
            descripcion=u'1 - Verificación final', tiempo=.2)
        _2_pruebas_fuerza = Tarea.objects.create(
            descripcion=u'2 - Pruebas de fuerza', tiempo=2)
        _3_pesaje = Tarea.objects.create(
            descripcion=u'3 - Pesaje', tiempo=.15)
        _4_inspeccion = Tarea.objects.create(
            descripcion=u'4 - Inspección visual', tiempo=.5)
        _5_prensado = Tarea.objects.create(
            descripcion=u'5 - Prensado', tiempo=1.5)
        _6_moldeado = Tarea.objects.create(
            descripcion=u'6 - Moldeado', tiempo=2)
        _6_1_1_cortado_tejido = Tarea.objects.create(
            descripcion=u'6.1.1 - Cortado Tejido', tiempo=.2)
        _6_1_2_laminado_tejido = Tarea.objects.create(
            descripcion=u'6.1.2 - Laminado Tejido', tiempo=.4)
        _6_2_1_extruccion_caucho = Tarea.objects.create(
            descripcion=u'6.2.1 - Extrucción Caucho', tiempo=.6)
        _6_2_2_obtencion_caucho = Tarea.objects.create(
            descripcion=u'6.2.2 - Obtención Caucho', tiempo=.4)
        _6_3_1_cortado_hilo_metalico = Tarea.objects.create(
            descripcion=u'6.3.1 - Cortado Hilo Metálico', tiempo=.1)
        _6_3_2_laminado_hilo_metalico = Tarea.objects.create(
            descripcion=u'6.3.2 - Laminado Hilo Metálico', tiempo=.4)
        _6_4_1_construccion_talones = Tarea.objects.create(
            descripcion=u'6.4.1 - Construcción de Talones', tiempo=2)

        _1_rayos_x = Maquina.objects.create(
                descripcion=u"1 - Rayos X")
        _2_variador_de_fuerza = Maquina.objects.create(
                descripcion=u"2 - Variador de Fuerza")
        _3_balanza = Maquina.objects.create(
                descripcion=u"3 - Balanza")
        _4_soprte_para_inspeccion = Maquina.objects.create(
                descripcion=u"4 - Soprte Para Inspección")
        _5_prensa_de_vulcanizado = Maquina.objects.create(
                descripcion=u"5 - Prensa de Vulcanizado")
        _6_moldeadora_de_neumaticos_1 = Maquina.objects.create(
                descripcion=u"6 - Moldeadora de Neumáticos 1")
        _6_moldeadora_de_neumaticos_2 = Maquina.objects.create(
                descripcion=u"6 - Moldeadora de Neumáticos 2")
        _6_1_cortadora_laminadora = Maquina.objects.create(
                descripcion=u"6.1 - Cortadora Laminadora")
        _6_2_1_extructora_de_caucho = Maquina.objects.create(
                descripcion=u"6.2.1 - Extructora de Caucho")
        _6_2_2_malaxador_banbury = Maquina.objects.create(
                descripcion=u"6.2.2 - Malaxador Banbury")
        _6_3_1_cortadora_de_hilo_metalico = Maquina.objects.create(
                descripcion=u"6.3.1 - Cortadora de Hilo Metálico")
        _6_3_2_calandria_laminadora_de_hilo_metalico = Maquina.objects.create(
                descripcion=u"6.3.2 - Calandria Laminadora de Hilo Metálico")
        _6_4_1_constructora_de_talones = Maquina.objects.create(
                descripcion=u"6.4.1 - Constructora de Talones")

        """
        Se indica qué recurso realiza qué tarea(s).
        """
        _1_rayos_x.add_tarea(_1_verificacion)
        _2_variador_de_fuerza.add_tarea(_2_pruebas_fuerza)
        _3_balanza.add_tarea(_3_pesaje)
        _4_soprte_para_inspeccion.add_tarea(_4_inspeccion)
        _5_prensa_de_vulcanizado.add_tarea(_5_prensado)
        _6_moldeadora_de_neumaticos_1.add_tarea(_6_moldeado)
        _6_moldeadora_de_neumaticos_2.add_tarea(_6_moldeado)
        _6_1_cortadora_laminadora.add_tarea(_6_1_1_cortado_tejido)
        _6_1_cortadora_laminadora.add_tarea(_6_1_2_laminado_tejido)
        _6_2_1_extructora_de_caucho.add_tarea(_6_2_1_extruccion_caucho)
        _6_2_2_malaxador_banbury.add_tarea(_6_2_2_obtencion_caucho)
        _6_3_1_cortadora_de_hilo_metalico.add_tarea(
                _6_3_1_cortado_hilo_metalico)
        _6_3_2_calandria_laminadora_de_hilo_metalico.add_tarea(
                _6_3_2_laminado_hilo_metalico)
        _6_4_1_constructora_de_talones.add_tarea(
                _6_4_1_construccion_talones)

        """
        Se indica de que tareas se compone el producto a realizar.
        """
        producto.add_tarea(_1_verificacion)
        producto.add_tarea(_2_pruebas_fuerza)
        producto.add_tarea(_3_pesaje)
        producto.add_tarea(_4_inspeccion)
        producto.add_tarea(_5_prensado)
        producto.add_tarea(_6_moldeado)
        producto.add_tarea(_6_1_1_cortado_tejido)
        producto.add_tarea(_6_1_2_laminado_tejido)
        producto.add_tarea(_6_2_1_extruccion_caucho)
        producto.add_tarea(_6_2_2_obtencion_caucho)
        producto.add_tarea(_6_3_1_cortado_hilo_metalico)
        producto.add_tarea(_6_3_2_laminado_hilo_metalico)
        producto.add_tarea(_6_4_1_construccion_talones)


        """
        Se define el flujo de trabajo a través de las dependencias:
        """
        producto.add_dependencia_tareas(
            tarea_anterior=_2_pruebas_fuerza, tarea=_1_verificacion)
        producto.add_dependencia_tareas(
            tarea_anterior=_3_pesaje, tarea=_2_pruebas_fuerza)
        producto.add_dependencia_tareas(
            tarea_anterior=_4_inspeccion, tarea=_3_pesaje)
        producto.add_dependencia_tareas(
            tarea_anterior=_5_prensado, tarea=_4_inspeccion)
        producto.add_dependencia_tareas(
            tarea_anterior=_6_moldeado, tarea=_5_prensado)
        producto.add_dependencia_tareas(
            tarea_anterior=_6_1_1_cortado_tejido, tarea=_6_moldeado)
        producto.add_dependencia_tareas(
            tarea_anterior=_6_2_1_extruccion_caucho, tarea=_6_moldeado)
        producto.add_dependencia_tareas(
            tarea_anterior=_6_3_1_cortado_hilo_metalico, tarea=_6_moldeado)
        producto.add_dependencia_tareas(
            tarea_anterior=_6_4_1_construccion_talones, tarea=_6_moldeado)
        producto.add_dependencia_tareas(
            tarea_anterior=_6_1_2_laminado_tejido, tarea=_6_1_1_cortado_tejido)
        producto.add_dependencia_tareas(
            tarea_anterior=_6_2_2_obtencion_caucho, tarea=_6_2_1_extruccion_caucho)
        producto.add_dependencia_tareas(
            tarea_anterior=_6_3_2_laminado_hilo_metalico, tarea=_6_3_1_cortado_hilo_metalico)

        """
        Se crea un pedido de 200 unidades del producto, se asocia un cronograma
        a dicho pedido y se realiza la planificación del mismo a partir del
        4 de diciembre del 2014 a las 8 de la mañana.
        """
        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,200)
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

