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


class ReplanificacionStandsTestCase(TestCase):

    def test_replanificacion_stands_loreal(self):
        """
        Esta prueba surje de demostrar la mejora inmediata que se 
        da en caso que uno particione los productos de un pedido en
        varios items. El tiempo de ejecución de este caso, sin partición 
        alguna crecería en forma exponencial.
        """

        calendario = CalendarioProduccion.get_instance()

        # se define calendario lu a vi de 8 a 8:30
        calendario.add_intervalos_laborables(
          dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES,
            DiaSemana.MIERCOLES,DiaSemana.JUEVES,DiaSemana.VIERNES],
          hora_desde=T(8), hora_hasta=T(12))

        producto = Producto.objects.create(descripcion='Stand Loreal')

        tarea_armado = Tarea.objects.create(
            descripcion='Armado', tiempo=180)
        tarea_embalaje = Tarea.objects.create(
            descripcion='Embalaje', tiempo=90)
        tarea_grafica_cenefas = Tarea.objects.create(
            descripcion='Grafica Cenefas', tiempo=120)
        tarea_pintura = Tarea.objects.create(
            descripcion='Pintura', tiempo=240)
        tarea_termoformado = Tarea.objects.create(
            descripcion='Termoformado', tiempo=30)

        maquina_mano_obra = Maquina.objects.create(descripcion='Mano de Obra')
        maquina_plotter = Maquina.objects.create(descripcion='Plotter')
        maquina_cabina_pintura = Maquina.objects.create(descripcion='Cabina Pintura')
        maquina_termoformadora_1 = Maquina.objects.create(descripcion='Termoformadora 1')
        maquina_termoformadora_2 = Maquina.objects.create(descripcion='Termoformadora 2')

        maquina_mano_obra.add_tarea(tarea_armado)
        maquina_mano_obra.add_tarea(tarea_embalaje)
        maquina_plotter.add_tarea(tarea_grafica_cenefas)
        maquina_cabina_pintura.add_tarea(tarea_pintura)
        maquina_termoformadora_1.add_tarea(tarea_termoformado)
        maquina_termoformadora_2.add_tarea(tarea_termoformado)

        producto.add_tarea(tarea_armado)
        producto.add_tarea(tarea_embalaje)
        producto.add_tarea(tarea_grafica_cenefas)
        producto.add_tarea(tarea_pintura)
        producto.add_tarea(tarea_termoformado)

        producto.add_dependencia_tareas(
            tarea_anterior=tarea_termoformado, tarea=tarea_grafica_cenefas)
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_termoformado, tarea=tarea_pintura)
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_grafica_cenefas, tarea=tarea_armado)
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_pintura, tarea=tarea_armado)
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_armado, tarea=tarea_embalaje)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,7)
        pedido.add_item(producto,7)

        cronograma = pedido.crear_cronograma()

        cronograma.planificar()
        cronograma.activar()

        intervalo = cronograma.get_intervalos().filter(
            tarea=tarea_armado).first()
        
        intervalo.cancelar()

        pedido.crear_cronograma().planificar()


