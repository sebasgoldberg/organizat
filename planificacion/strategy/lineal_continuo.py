# coding=utf-8
from pulp import *
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from math import ceil
from planificacion.strategy.base import PlanificadorStrategy
from planificacion.strategy.utils import add_keys_to_dict
from planificacion.dependencias import GerenciadorDependencias
import planificacion.models 
from django.core.exceptions import ValidationError
import datetime
import logging

logger = logging.getLogger(__name__)

C_100_ANYOS_EN_MINUTOS = 52560000

class ModeloLinealNoResuelto(Exception):
  pass

class PlanificadorLinealContinuo(PlanificadorStrategy):

  modelo = None
  tiempos_maquinas = {}
  is_maximo_tiempo_maquina = {}
  tiempo_maquina_tarea_pedido_producto = {}

  def get_tiempo_infinito(self):
    return C_100_ANYOS_EN_MINUTOS

  def def_tiempo_maquina_maximo_maquinas(self):

    for maquina in self.get_grupo_maquinas_planificado():
      tiempo_maquina = self.tiempos_maquinas[maquina.id]
      is_maximo_tiempo_maquina = self.is_maximo_tiempo_maquina[maquina.id]
      # TMi - M(1-Y_MAX_Mi) <= T_MAX_MAQ <= TMi + M(1-Y_MAX_Mi)
      self.modelo += tiempo_maquina + \
        (1-is_maximo_tiempo_maquina)*self.get_tiempo_infinito() - \
        self.tiempo_maquina_maximo >= 0, "Cota superior tiempo maquina %s al tiempo de maquina maximo" % maquina.id
      self.modelo += tiempo_maquina - \
        (1-is_maximo_tiempo_maquina)*self.get_tiempo_infinito() - \
        self.tiempo_maquina_maximo <= 0, "Cota inferior tiempo maquina %s al tiempo de maquina maximo" % maquina.id
      for otra_maquina in self.get_grupo_maquinas_planificado():
        if maquina.id == otra_maquina.id:
          continue
        tiempo_otra_maquina = self.tiempos_maquinas[otra_maquina.id]
        self.modelo +=\
          tiempo_maquina + (1-is_maximo_tiempo_maquina)*self.get_tiempo_infinito() - \
            tiempo_otra_maquina >= 0, "La maquina %s es mayor a la maquina %s." % (maquina.id, otra_maquina.id)
    self.modelo += lpSum(self.is_maximo_tiempo_maquina.values()) == 1, "Existira un solo maximo" 

  def def_tiempo_insumido_maquinas(self):

    T_MTPD = self.tiempo_maquina_tarea_pedido_producto

    for maquina in self.get_grupo_maquinas_planificado():
      self.modelo += lpSum([
        T_MTPD[maquina.id][tarea.id][producto.id][pedido.id]
          for pedido in self.cronograma.get_pedidos()
            for producto in pedido.get_productos()
              for tarea in producto.get_tareas_maquina(maquina) ]) - \
        self.tiempos_maquinas[maquina.id] == 0,\
          "Tiempo de la maquina %s" % maquina.id

  def get_tareas_producto_segun_grupo_maquinas(self, producto):

    tareas = set()

    for maquina in self.grupo_maquinas_planificado:
      for tarea in producto.get_tareas_maquina(maquina):
        tareas.add(tarea)

    return tareas

  def get_maquinas_tarea_producto(self, tarea, producto):
    for maquina in self.cronograma.get_maquinas_tarea_producto(tarea, producto):
      if maquina in self.get_grupo_maquinas_planificado():
        yield maquina

  def def_cumplir_cantidad_producir(self):

    T_MTPD = self.tiempo_maquina_tarea_pedido_producto

    for pedido in self.cronograma.get_pedidos():
      for item in pedido.get_items():
        producto = item.producto
        for tarea in self.get_tareas_producto_segun_grupo_maquinas(producto):
          self.modelo += lpSum([
            T_MTPD[maquina.id][tarea.id][producto.id][pedido.id] /\
            tarea.get_tiempo(maquina,producto)
            for maquina in self.get_maquinas_tarea_producto(tarea, producto)
            ]) - item.get_cantidad_no_planificada(tarea)\
            == 0, "La suma del tiempo de produccion en maquinas para tarea %s, para producto %s, pedido %s, debe corresponderse con la cantidad de tarea a producir" % (
              tarea.id, producto.id, pedido.id)

  def definir_restricciones(self):

    self.def_tiempo_maquina_maximo_maquinas()
    self.def_tiempo_insumido_maquinas()
    self.def_cumplir_cantidad_producir()

  def get_grupo_maquinas_planificado(self):
    return self.grupo_maquinas_planificado

  def __init__(self, *args, **kwargs):
    PlanificadorStrategy.__init__(self, *args, **kwargs)
    self.tiempos_intervalos_registrados = {}

  def registrar_tiempos_maquinas_planificadas(self):

    for maquina in self.get_grupo_maquinas_planificado():

      for pedido in self.cronograma.get_pedidos():
        for producto in pedido.get_productos():
          gerenciador_dependencias = GerenciadorDependencias(self.cronograma, producto, pedido)
          for tarea in producto.get_tareas_maquina(maquina):
            clave = (maquina.id, tarea.id, producto.id, pedido.id)
            if clave in self.tiempos_intervalos_registrados:
              continue
            tiempo = self.tiempo_maquina_tarea_pedido_producto[
              maquina.id][tarea.id][producto.id][pedido.id].value()
            if tiempo > 0:
              self.tiempos_intervalos_registrados[clave] = tiempo

  def definir_variables(self):
    
    self.tiempos_maquinas = {}
    self.is_maximo_tiempo_maquina = {}
    self.tiempo_maquina_tarea_pedido_producto = {}

    for maquina in self.get_grupo_maquinas_planificado():
      self.tiempos_maquinas[maquina.id] = LpVariable(
        "T_MAQ_%s" % maquina.id,0)
      self.is_maximo_tiempo_maquina[maquina.id] = LpVariable(
        "Y_MAX_T_MAQ_%s" % maquina.id,0,1,LpInteger)

    for maquina in self.get_grupo_maquinas_planificado():
      # Se obtienen solo las tareas que pertencen a la máquina iterada
      for tarea in maquina.get_tareas():
        for pedido in self.cronograma.get_pedidos():
          for producto in pedido.get_productos_maquina_tarea(maquina,tarea):

            add_keys_to_dict(
              self.tiempo_maquina_tarea_pedido_producto,
              [maquina.id,tarea.id,producto.id,pedido.id])

            self.tiempo_maquina_tarea_pedido_producto[
              maquina.id][tarea.id][producto.id][pedido.id] = LpVariable(
                "T_M%s_T%s_P%s_D%s" % \
                (maquina.id, tarea.id, pedido.id, producto.id), 0)

  def definir_funcional(self):

    self.tiempo_maquina_maximo = LpVariable("T_MAX_MAQ",0)

    # Creamos la función objetivo
    self.modelo += self.tiempo_maquina_maximo, "Tiempo total de produccion"

  def definir_modelo(self):

    # Creamos el modelo e indicamos que se trata de un problema de búsqueda de mínimo
    self.modelo = LpProblem('Planificar cronograma %s' % self.cronograma.id,LpMinimize)

    self.definir_funcional()

    self.definir_variables()

    self.definir_restricciones()

    #self.modelo.writeLP("/tmp/djprod.lp")

  def is_modelo_resuelto(self):
    return (self.modelo and self.modelo.status == LpStatusOptimal)

  def completar_cronograma(self):

    for pedido in self.cronograma.get_pedidos():
      for producto in pedido.get_productos():
        gerenciador_dependencias = GerenciadorDependencias(self.cronograma, producto, pedido)
        for tarea in producto.get_tareas_ordenadas_por_dependencia():
          for maquina in self.cronograma.get_maquinas_tarea_producto(tarea, producto):
            clave = (maquina.id, tarea.id, producto.id, pedido.id)
            if clave in self.tiempos_intervalos_registrados:
              tiempo = self.tiempos_intervalos_registrados[clave]
              logger.debug(_(u'Se agregan intervalos a cronograma para:\n'+
                u'\tmaquina: %s\ttarea: %s\tproducto: %s\tpedido: %s\ttiempo: %s') % (
                  maquina, tarea, producto, pedido, tiempo))
              gerenciador_dependencias.add_intervalos_to_cronograma(
                maquina=maquina, tarea=tarea, tiempo=tiempo)

  def get_maquinas_relacionadas_por_tareas(self):
    """
    Si M1 tiene las tareas T1 y T2, M2 tiene las tareas T3 y T4 y
    M5 tiene la tarea T1, entonces se obtendrán 2 listados:
    - [M1, M3]
    - [M2]
    """

    if not self.cronograma.optimizar_planificacion:
      yield self.cronograma.get_maquinas()
      return

    pedidos = self.cronograma.get_pedidos()

    maquinas = set(self.cronograma.get_maquinas())

    while len(maquinas)>0:

      conjunto_maquinas = set()

      for maquina in maquinas:

        if len(conjunto_maquinas) == 0:
          conjunto_maquinas.add(maquina)
          tareas_compartidas = maquina.get_tareas_pedidos(pedidos)
        else:
          tareas_maquina = maquina.get_tareas_pedidos(pedidos)
          if len(tareas_compartidas & tareas_maquina) <> 0:
            conjunto_maquinas.add(maquina)
            tareas_compartidas = tareas_compartidas | tareas_maquina

      yield conjunto_maquinas
      maquinas = maquinas - conjunto_maquinas

  def planificar(self):
    
    for maquinas in self.get_maquinas_relacionadas_por_tareas():

      self.grupo_maquinas_planificado = maquinas

      self.definir_modelo()

      self.modelo.solve()

      if not self.is_modelo_resuelto():
        raise ModeloLinealNoResuelto(_(u'No a podido resolverse el modelo lineal.'))

      self.registrar_tiempos_maquinas_planificadas()

    self.completar_cronograma()

