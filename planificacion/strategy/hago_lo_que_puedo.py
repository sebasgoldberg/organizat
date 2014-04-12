# coding=utf-8
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from math import ceil
from planificacion.strategy.base import PlanificadorStrategy
    
class PlanificadorHagoLoQuePuedo(PlanificadorStrategy):

  def planificar(self):
    """
    La idea es:
    1) Tomar la cantidad de horas a realizar en cada tarea.
    2) Obtener las maquinas posibles para la tarea y cronograma dados.
    3) crear tantos intervalos como sean necesarios.
    """
    maquinas_cronograma = self.cronograma.get_maquinas()

    for pedido in self.cronograma.get_pedidos():
      for item_pedido in pedido.itempedido_set.all():
        producto = item_pedido.producto
        cantidad_a_producir = item_pedido.cantidad
        for tarea in producto.get_tareas():
          for maquina in tarea.get_maquinas():
            if maquina in maquinas_cronograma:
              cantidad_intervalos = int(ceil( tarea.get_tiempo(maquina,producto) * cantidad_a_producir / self.cronograma.intervalo_tiempo ))
              cantidad_tarea = cantidad_a_producir / cantidad_intervalos
              acumulado_tarea = 0
              for i in range(1,cantidad_intervalos+1):
                acumulado_tarea += cantidad_tarea
                self.cronograma.add_intervalo_al_final(maquina, tarea, producto, pedido, acumulado_tarea)
              break

