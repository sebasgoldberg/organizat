# coding=utf-8
from pulp import *
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from math import ceil
from planificacion.strategy.base import PlanificadorStrategy
from planificacion.strategy.utils import add_keys_to_dict

C_100_ANYOS_EN_MINUTOS = 52560000

class PlanificadorLinealContinuo(PlanificadorStrategy):

  modelo = None
  tiempos_maquinas = {}
  is_maximo_tiempo_maquina = {}
  tiempo_maquina_tarea_pedido_producto = {}

  def get_tiempo_infinito(self):
    return C_100_ANYOS_EN_MINUTOS

  def def_tiempo_maquina_maximo_maquinas(self):

    for maquina in self.cronograma.get_maquinas():
      tiempo_maquina = self.tiempos_maquinas[maquina.id]
      is_maximo_tiempo_maquina = self.is_maximo_tiempo_maquina[maquina.id]
      # TMi - M(1-Y_MAX_Mi) <= T_MAX_MAQ <= TMi + M(1-Y_MAX_Mi)
      self.modelo += tiempo_maquina + \
        (1-is_maximo_tiempo_maquina)*self.get_tiempo_infinito() - \
        self.tiempo_maquina_maximo >= 0, "Cota superior tiempo maquina %s al tiempo de maquina maximo" % maquina.id
      self.modelo += tiempo_maquina - \
        (1-is_maximo_tiempo_maquina)*self.get_tiempo_infinito() - \
        self.tiempo_maquina_maximo <= 0, "Cota inferior tiempo maquina %s al tiempo de maquina maximo" % maquina.id
      for otra_maquina in self.cronograma.get_maquinas():
        if maquina.id == otra_maquina.id:
          continue
        tiempo_otra_maquina = self.tiempos_maquinas[otra_maquina.id]
        self.modelo +=\
          tiempo_maquina + (1-is_maximo_tiempo_maquina)*self.get_tiempo_infinito() - \
            tiempo_otra_maquina >= 0, "La maquina %s es mayor a la maquina %s." % (maquina.id, otra_maquina.id)
    self.modelo += lpSum(self.is_maximo_tiempo_maquina.values()) == 1, "Existira un solo maximo" 

  def def_tiempo_insumido_maquinas(self):

    T_MTPD = self.tiempo_maquina_tarea_pedido_producto

    for maquina in self.cronograma.get_maquinas():
      self.modelo += lpSum([
        T_MTPD[maquina.id][tarea.id][producto.id][pedido.id]
          for pedido in self.cronograma.get_pedidos()
            for producto in pedido.get_productos()
              for tarea in producto.get_tareas_maquina(maquina) ]) - \
        self.tiempos_maquinas[maquina.id] == 0, "Tiempo de la maquina %s" % maquina.id

  def def_cumplir_cantidad_producir(self):

    T_MTPD = self.tiempo_maquina_tarea_pedido_producto

    for pedido in self.cronograma.get_pedidos():
      for producto in pedido.get_productos():
        for tarea in producto.get_tareas():
          self.modelo += lpSum([
            T_MTPD[maquina.id][tarea.id][producto.id][pedido.id] /\
            tarea.get_tiempo(maquina,producto)
            for maquina in tarea.get_maquinas_producto(producto)
            ]) - tarea.get_cantidad_producir(producto, pedido)\
            == 0, "La suma del tiempo de produccion en maquinas para tarea %s, para producto %s, pedido %s, debe corresponderse con la cantidad de tarea a producir" % (
              tarea.id, producto.id, pedido.id)

  def definir_restricciones(self):

    self.def_tiempo_maquina_maximo_maquinas()
    self.def_tiempo_insumido_maquinas()
    self.def_cumplir_cantidad_producir()

  def definir_variables(self):

    for maquina in self.cronograma.get_maquinas():
      self.tiempos_maquinas[maquina.id] = LpVariable(
        "T_MAQ_%s" % maquina.id,0)
      self.is_maximo_tiempo_maquina[maquina.id] = LpVariable(
        "Y_MAX_T_MAQ_%s" % maquina.id,0,1,LpInteger)

    for maquina in self.cronograma.get_maquinas():
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
                (maquina.id, tarea.id, pedido.id, producto.id),0)

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

  def completar_cronograma(self):
    for maquina in self.cronograma.get_maquinas():
      # Se obtienen solo las tareas que pertencen a la máquina iterada
      instante = 0
      for tarea in maquina.get_tareas():
        for pedido in self.cronograma.get_pedidos():
          for producto in pedido.get_productos_maquina_tarea(maquina,tarea):
            tiempo = self.tiempo_maquina_tarea_pedido_producto[
              maquina.id][tarea.id][producto.id][pedido.id].value()
            if tiempo > 0:
              instante+=1
              self.cronograma.add_intervalo(instante,maquina,tarea,pedido,producto,
                tiempo/float(tarea.get_tiempo(maquina,producto)),tiempo_intervalo=ceil(tiempo))

  def planificar(self):
    
    self.definir_modelo()

    self.modelo.solve()

    if not self.is_modelo_resuelto():
      raise ModeloLinealNoResuelto(_(u'No a podido resolverse el modelo lineal.'))

    self.completar_cronograma()

    for v in self.modelo.variables():
      print v.name, "=", v.varValue

    print "Tiempo de produccion = ", value(self.modelo.objective)

