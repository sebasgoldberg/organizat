# coding=utf-8
from pulp import *
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from math import ceil
from planificacion.strategy.base import PlanificadorStrategy
from planificacion.strategy.utils import add_keys_to_dict
import planificacion.models 
from django.core.exceptions import ValidationError
import datetime
import logging
from decimal import Decimal as D

logger = logging.getLogger(__name__)

C_100_ANYOS_EN_MINUTOS = 52560000

class ModeloLinealNoResuelto(ValidationError):
  pass

class PlanificadorLinealContinuo(PlanificadorStrategy):

  modelo = None
  tiempos_maquinas = {}
  is_maximo_tiempo_maquina = {}
  tiempo_maquina_tarea_item = {}

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

  def get_tiempo_intervalos_activos_y_finalizados(self, maquina):
    """
    Obtiene la suma de los tiempos de intervalos activos y
    finalizados a partir de la fecha de inicio del cronograma.
    El tiempo devuelto es en minutos.
    """
    intervalos = maquina.get_intervalos_activos(
        ).filter(
            fecha_hasta__gt=self.cronograma.fecha_inicio)

    tiempo = D(0)

    for i in intervalos:
      if i.fecha_desde < self.cronograma.fecha_inicio:
        tiempo += D((i.fecha_hasta - 
            self.cronograma.fecha_inicio).seconds())/D(60)
      else:
        tiempo += D(i.tiempo_intervalo)

    return tiempo

  def def_tiempo_insumido_maquinas(self):

    T_MTI = self.tiempo_maquina_tarea_item

    for maquina in self.get_grupo_maquinas_planificado():
      self.modelo += ( lpSum([
        T_MTI[maquina.id][tarea.id][item.id]
          for pedido in self.cronograma.get_pedidos()
            for item in pedido.get_items()
              for tarea in item.producto.get_tareas_maquina(maquina) ]) -
        self.tiempos_maquinas[maquina.id] + 
        self.get_tiempo_intervalos_activos_y_finalizados(maquina) == 0,
          "Tiempo de la maquina %s" % maquina.id )

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

  def get_cantidad_no_planificada(self, item, tarea):
    cantidad = D(item.get_cantidad_no_planificada(tarea))
    if cantidad < self.cronograma.get_tolerancia(item.cantidad):
      return 0
    return cantidad

  def def_cumplir_cantidad_producir(self):

    T_MTI = self.tiempo_maquina_tarea_item

    for pedido in self.cronograma.get_pedidos():
      for item in pedido.get_items():
        for tarea in self.get_tareas_producto_segun_grupo_maquinas(item.producto):
          self.modelo += lpSum([
            T_MTI[maquina.id][tarea.id][item.id] /\
            D(tarea.get_tiempo(maquina,item.producto))
            for maquina in self.get_maquinas_tarea_producto(tarea, item.producto)
            ]) - self.get_cantidad_no_planificada(item, tarea)\
            == 0, "La suma del tiempo de produccion en maquinas para tarea %s, item %s, debe corresponderse con la cantidad de tarea a producir" % (tarea.id, item.id)

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
        for item in pedido.get_items():
          for tarea in item.producto.get_tareas_maquina(maquina):
            clave = (maquina.id, tarea.id, item.id)
            if clave in self.tiempos_intervalos_registrados:
              continue
            tiempo = self.tiempo_maquina_tarea_item[
              maquina.id][tarea.id][item.id].value()
            if tiempo > 0:
              self.tiempos_intervalos_registrados[clave] = tiempo

  def definir_variables(self):
    
    self.tiempos_maquinas = {}
    self.is_maximo_tiempo_maquina = {}
    self.tiempo_maquina_tarea_item = {}

    for maquina in self.get_grupo_maquinas_planificado():
      self.tiempos_maquinas[maquina.id] = LpVariable(
        "T_MAQ_%s" % maquina.id,0)
      self.is_maximo_tiempo_maquina[maquina.id] = LpVariable(
        "Y_MAX_T_MAQ_%s" % maquina.id,0,1,LpInteger)

    for maquina in self.get_grupo_maquinas_planificado():
      # Se obtienen solo las tareas que pertencen a la máquina iterada
      for tarea in maquina.get_tareas():
        for pedido in self.cronograma.get_pedidos():
          for item in pedido.get_items_maquina_tarea(maquina,tarea):

            add_keys_to_dict(
              self.tiempo_maquina_tarea_item,
              [maquina.id,tarea.id,item.id])

            self.tiempo_maquina_tarea_item[
              maquina.id][tarea.id][item.id] = LpVariable(
                "T_M%s_T%s_I%s" % \
                (maquina.id, tarea.id, item.id), 0)

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

    self.modelo.writeLP("/tmp/djprod.lp")

  def is_modelo_resuelto(self):
    return (self.modelo and self.modelo.status == LpStatusOptimal)

  #@profile
  def completar_cronograma(self):

    for pedido in self.cronograma.get_pedidos():
      for item in pedido.get_items():
        gerenciador_dependencias = self.cronograma.get_gerenciador_dependencias(item)
        # Se obtienen las tareas ordenas por dependencia.
        for tarea in item.producto.get_tareas_ordenadas_por_dependencia():
          for maquina in self.cronograma.get_maquinas_tarea_producto(tarea, item.producto):
            clave = (maquina.id, tarea.id, item.id)
            if clave in self.tiempos_intervalos_registrados:
              tiempo = self.tiempos_intervalos_registrados[clave]
              logger.debug(_(u'Se agregan intervalos a cronograma para:\n'+
                u'\tmaquina: %s\ttarea: %s\titem: %s\ttiempo: %s') % (
                  maquina, tarea, item, tiempo))
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

  #@profile
  def planificar(self):
    
    for maquinas in self.get_maquinas_relacionadas_por_tareas():

      self.grupo_maquinas_planificado = maquinas

      self.definir_modelo()

      # Redirige la salida a /dev/null
      self.modelo.setSolver()
      self.modelo.solver.msg = False

      self.modelo.solve()

      if not self.is_modelo_resuelto():
        raise ModeloLinealNoResuelto(_(u'No a podido resolverse el modelo lineal.'))

      self.registrar_tiempos_maquinas_planificadas()

    self.completar_cronograma()

