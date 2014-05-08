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
                (maquina.id, tarea.id, pedido.id, producto.id),self.cronograma.tiempo_minimo_intervalo)

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
    for pedido in self.cronograma.get_pedidos():
      for producto in pedido.get_productos():
        gerenciador_dependencias = GerenciadorDependencias(self.cronograma, producto, pedido)
        for tarea in producto.get_tareas_ordenadas_por_dependencia():
          for maquina in producto.get_maquinas_tarea(tarea):
            tiempo = self.tiempo_maquina_tarea_pedido_producto[
              maquina.id][tarea.id][producto.id][pedido.id].value()
            if tiempo > 0:
              gerenciador_dependencias.add_intervalos_to_cronograma(
                maquina=maquina, tarea=tarea, tiempo=tiempo)

  def optimizar_intervalo(self, intervalo):

    fecha_desde_inicial = intervalo.fecha_desde
    fecha_desde_final = intervalo.fecha_desde

    try:
      hueco = intervalo.get_hueco_adyacente_anterior()
      cota_inferior = 0
      cota_superior = hueco.tiempo.total_seconds() - 1
      fecha_desde = hueco.fecha_desde

      while (cota_inferior <= cota_superior):

        incremento_temporal = int((cota_inferior + cota_superior) / 2)

        try:
          intervalo.fecha_desde = fecha_desde +\
            datetime.timedelta(seconds=int(incremento_temporal))
          intervalo.clean()
          intervalo.save()
          cota_superior = incremento_temporal - 1
          fecha_desde_final = intervalo.fecha_desde
        except ValidationError:
          cota_inferior = incremento_temporal + 1
 
    except planificacion.models.HuecoAdyacenteAnteriorNoExiste:
      pass

    return fecha_desde_inicial > fecha_desde_final

  def optimizar_cronograma_maquina(self, maquina):
    cronograma_optimizado = False
    for intervalo in self.cronograma.get_intervalos_maquina(maquina).order_by('fecha_desde'):
      intervalo_optimizado = self.optimizar_intervalo(intervalo)
      if intervalo_optimizado:
        cronograma_optimizado = True
    return cronograma_optimizado

  def optimizar_cronograma(self):

    optimizacion_realizada = True

    while (optimizacion_realizada):
      optimizacion_realizada = False
      for maquina in self.cronograma.get_maquinas():
        optimizacion_realizada_maquina = self.optimizar_cronograma_maquina(maquina)
        if optimizacion_realizada_maquina:
          optimizacion_realizada = True

  def planificar(self):
    
    self.definir_modelo()

    self.modelo.solve()

    if not self.is_modelo_resuelto():
      # @todo Agregar la posibilidad de mostrar el mensaje en caso que exista request
      #messages.warning(request, _(u'No se ha podido resolver el modelo. Se anula tiempo mínimo del cronograma y se intenta nuevamente.'))
      self.cronograma.tiempo_minimo_intervalo = 0
      self.cronograma.clean()
      self.cronograma.save()
      self.definir_modelo()
      self.modelo.solve()

    if not self.is_modelo_resuelto():
      raise ModeloLinealNoResuelto(_(u'No a podido resolverse el modelo lineal.'))

    self.completar_cronograma()

    if self.cronograma.optimizar_planificacion:
      self.optimizar_cronograma()