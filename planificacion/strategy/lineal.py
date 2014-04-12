# coding=utf-8
from pulp import *
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from math import ceil
from planificacion.strategy.base import PlanificadorStrategy

def add_keys_to_dict(dictionary,keys):
  if len(keys) == 0:
    return
  if not dictionary.has_key(keys[0]):
    dictionary[keys[0]] = {}
  add_keys_to_dict(dictionary[keys[0]],keys[1:])
    
PRIMER_INSTANTE = 1

class PlanificadorModeloLineal(PlanificadorStrategy):

  max_instante = None
  modelo = None
  # Variables
  tiempos_maquinas = {}
  is_maximo_tiempo_maquina = {}
  is_instante_maquina_tarea_producto_pedido = {}
  cantidad_tareas_producidas = {}
  cantidad_tarea_en_instante = {}

  def get_max_instante(self):
    return self.max_instante

  def get_incremento_instante(self):
    return self.cronograma.intervalo_tiempo

  def get_tiempo_infinito(self):
    return ( self.get_max_instante() + 1 ) * self.get_incremento_instante()

  def get_instantes(self):
    return range(1,self.get_max_instante()+1)

  def def_tiempo_maquina_maximo_maquinas(self):

    for maquina in self.cronograma.get_maquinas():
      tiempo_maquina = self.tiempos_maquinas[maquina.id]
      is_maximo_tiempo_maquina = self.is_maximo_tiempo_maquina[maquina.id]
      self.modelo += tiempo_maquina + \
        (1-is_maximo_tiempo_maquina)*self.get_tiempo_infinito() - \
        self.tiempo_maquina_maximo >= 0, "Cota superior tiempo maquina %s al tiempo de maquina maximo" % maquina.id
      self.modelo += tiempo_maquina - \
        is_maximo_tiempo_maquina*self.get_tiempo_infinito() - \
        self.tiempo_maquina_maximo <= 0, "Cota inferior tiempo maquina %s al tiempo de maquina maximo" % maquina.id
    self.modelo += lpSum(self.is_maximo_tiempo_maquina.values()) == 1, "Existira un solo maximo" 

  def def_tiempo_insumido_maquinas(self):

    Y_MTPD = self.is_instante_maquina_tarea_producto_pedido

    for maquina in self.cronograma.get_maquinas():
      self.modelo += lpSum([
        Y_MTPD[instante][maquina.id][tarea.id][producto.id][pedido.id] * \
          self.get_incremento_instante()
            for pedido in self.cronograma.get_pedidos()
              for producto in pedido.get_productos()
                for tarea in producto.get_tareas_maquina(maquina)
                  for instante in self.get_instantes() ]) - \
        self.tiempos_maquinas[maquina.id] == 0, "Tiempo de la maquina %s" % maquina.id

  def def_una_tarea_por_maquina_por_instante(self):
    
    Y_MTPD = self.is_instante_maquina_tarea_producto_pedido

    for instante in self.get_instantes():
      for maquina in self.cronograma.get_maquinas():
        self.modelo += lpSum([
          Y_MTPD[instante][maquina.id][tarea.id][producto.id][pedido.id] 
          for pedido in self.cronograma.get_pedidos()
            for producto in pedido.get_productos()
              for tarea in producto.get_tareas_maquina(maquina) ]) - \
          1 <= 0, "Una unica tarea en el instante %s en la maquina %s." % (instante, maquina.id)

  def def_cumplir_cantidad_producir(self):

    Y_MTPD = self.is_instante_maquina_tarea_producto_pedido

    for pedido in self.cronograma.get_pedidos():
      for producto in pedido.get_productos():
        for tarea in producto.get_tareas():
          self.modelo += lpSum([
            Y_MTPD[instante][maquina.id][tarea.id][producto.id][pedido.id] *\
            self.get_incremento_instante() /\
            tarea.get_tiempo(maquina,producto)
            for maquina in tarea.get_maquinas_producto(producto)
              for instante in self.get_instantes()
            ]) - self.cantidad_tareas_producidas[tarea.id][producto.id][pedido.id]\
            == 0, "Cantidad producida de tarea %s, para producto %s, pedido %s." % (
              tarea.id, producto.id, pedido.id)
          self.modelo += self.cantidad_tareas_producidas[tarea.id][producto.id][pedido.id] -\
            tarea.get_cantidad_producir(producto, pedido) >= 0,\
            "La cantidad producida de la tarea %s, producto %s, pedido %s debe ser mayor o igual que la cantidad a producir del producto %s del pedido %s." % (
            tarea.id,producto.id,pedido.id,producto.id,pedido.id)

  def def_cant_tarea_hasta_instante(self):

    Y_MTPD = self.is_instante_maquina_tarea_producto_pedido

    for pedido in self.cronograma.get_pedidos():
      for producto in pedido.get_productos():
        for tarea in producto.get_tareas():
          for instante in self.get_instantes():
            if instante == PRIMER_INSTANTE:
              # El primer instante es simplemente la suma de cantidad de tarea realizada en cada máquina.
              self.modelo +=\
                self.cantidad_tarea_en_instante[tarea.id][producto.id][pedido.id][instante] -\
                lpSum([\
                  Y_MTPD[instante][maquina.id][tarea.id][producto.id][pedido.id] *\
                  self.get_incremento_instante() /\
                  tarea.get_tiempo(maquina,producto)
                  for maquina in self.cronograma.get_maquinas_tarea_producto(tarea,producto)]) == 0,\
                    "Cantidad de tarea %s para el producto %s del pedido %s en hasta el instante %s." %\
                    (tarea.id, producto.id, pedido.id, instante)
            else:
              # En el resto de los instantes es simplemente la suma de cantidad de tarea 
              # realizada en cada máquina, mas la tarea realizada hasta el instante anterior.
              self.modelo +=\
                self.cantidad_tarea_en_instante[tarea.id][producto.id][pedido.id][instante] -\
                self.cantidad_tarea_en_instante[tarea.id][producto.id][pedido.id][instante-1] -\
                lpSum([\
                  Y_MTPD[instante][maquina.id][tarea.id][producto.id][pedido.id] *\
                  self.get_incremento_instante() /\
                  tarea.get_tiempo(maquina,producto)
                  for maquina in self.cronograma.get_maquinas_tarea_producto(tarea,producto)]) == 0,\
                    "Cantidad de tarea %s para el producto %s del pedido %s en hasta el instante %s." %\
                    (tarea.id, producto.id, pedido.id, instante)
    

  def def_secuencia_tareas(self):
    for pedido in self.cronograma.get_pedidos():
      for producto in pedido.get_productos():
        for tarea in producto.get_tareas():
          for tarea_anterior in tarea.get_anteriores(producto):
            for instante in self.get_instantes():
              self.modelo +=\
                self.cantidad_tarea_en_instante[tarea_anterior.id][producto.id][pedido.id][instante] -\
                self.cantidad_tarea_en_instante[tarea.id][producto.id][pedido.id][instante] >\
                0, "La tarea %s debe ser anterior a la tarea %s." % (tarea_anterior.id, tarea.id)

  def definir_variables(self):

    for maquina in self.cronograma.get_maquinas():
      self.tiempos_maquinas[maquina.id] = LpVariable(
        "T_MAQ_%s" % maquina.id,0)
      self.is_maximo_tiempo_maquina[maquina.id] = LpVariable(
        "Y_MAX_T_MAQ_%s" % maquina.id,0,1,LpInteger)

    for instante in self.get_instantes():
      for maquina in self.cronograma.get_maquinas():
        # Se obtienen solo las tareas que pertencen a la máquina iterada
        for tarea in maquina.get_tareas():
          for pedido in self.cronograma.get_pedidos():
            for producto in pedido.get_productos_maquina_tarea(maquina,tarea):
              add_keys_to_dict(
                self.is_instante_maquina_tarea_producto_pedido,
                [instante,maquina.id,tarea.id,producto.id,pedido.id])
              self.is_instante_maquina_tarea_producto_pedido[
                instante][maquina.id][tarea.id][producto.id][pedido.id] = LpVariable(
                  "Y_I%s_M%s_T%s_P%s_D%s" % \
                  (instante, maquina.id, tarea.id, pedido.id, producto.id),0,1,LpInteger)

    for pedido in self.cronograma.get_pedidos():
      for producto in pedido.get_productos():
        for tarea in producto.get_tareas():
          # Cantidad de tarea a producir, por producto, por pedido
          add_keys_to_dict(
            self.cantidad_tareas_producidas,
            [tarea.id,producto.id,pedido.id])
          self.cantidad_tareas_producidas[tarea.id][producto.id][pedido.id] =\
            LpVariable("CANT_T%s_P%s_D%s" % \
              (tarea.id, producto.id, pedido.id), 0)

          for instante_hasta in self.get_instantes():
            # Cantidad de tarea producida, hasta el instante r, por producto, por pedido
            add_keys_to_dict(self.cantidad_tarea_en_instante,
              [tarea.id, producto.id, pedido.id, instante_hasta])
            self.cantidad_tarea_en_instante[tarea.id][producto.id][pedido.id][instante_hasta] = \
              LpVariable("CANT_T%s_P%s_D%s_HI%s" % \
                (tarea.id, producto.id, pedido.id, instante_hasta), 0)

  def definir_funcional(self):

    self.tiempo_maquina_maximo = LpVariable("T_MAX_MAQ",0)

    # Creamos la función objetivo
    self.modelo += self.tiempo_maquina_maximo, "Tiempo total de produccion"

  def definir_restricciones(self):

    self.def_tiempo_maquina_maximo_maquinas()
    self.def_tiempo_insumido_maquinas()
    self.def_una_tarea_por_maquina_por_instante()
    self.def_cumplir_cantidad_producir()
    self.def_cant_tarea_hasta_instante()
    self.def_secuencia_tareas()

  def definir_modelo(self):
    """
    @todo Ver: https://pythonhosted.org/PuLP/CaseStudies/a_sudoku_problem.html
    """
    # Creamos el modelo e indicamos que se trata de un problema de búsqueda de mínimo
    self.modelo = LpProblem('Planificar cronograma %s' % self.cronograma.id,LpMinimize)

    self.definir_funcional()

    self.definir_variables()

    self.definir_restricciones()

    self.modelo.writeLP("/tmp/djprod.lp")

  def is_modelo_resuelto(self):
    return (self.modelo and self.modelo.status == LpStatusOptimal)

  def calcular_cotas_instante(self):

    self.cota_instante_inferior = 1

    tiempo_secuencial_total = 0

    for pedido in self.cronograma.get_pedidos():
      for item in pedido.get_items():
        for tarea in item.producto.get_tareas():
          tiempo_secuencial_total +=\
            item.cantidad * tarea.get_tiempo_maximo(item.producto)

    self.cota_instante_superior =\
      ceil( tiempo_secuencial_total / self.get_incremento_instante() )

  def resolver_modelo_busqueda_binaria(self):
    
    self.calcular_cotas_instante()

    while (self.cota_instante_inferior <= self.cota_instante_superior):

      self.max_instante = int(( self.cota_instante_inferior + self.cota_instante_superior ) / 2)

      self.definir_modelo()

      self.modelo.solve()

      if self.is_modelo_resuelto():
        # @todo: Ver si es necesario seguir buscando de forma de decrementar
        # la cota superior.
        break

      self.cota_instante_inferior = self.max_instante + 1

  def resolver_modelo_busqueda_secuencial(self):
    
    self.calcular_cotas_instante()

    self.max_instante = self.cota_instante_inferior

    while (self.max_instante <= self.cota_instante_superior):

      self.definir_modelo()

      self.modelo.solve()

      if self.is_modelo_resuelto():
        # @todo: Ver si es necesario seguir buscando de forma de decrementar
        # la cota superior.
        break

      self.max_instante += 1


  def completar_cronograma(self):
    
    for instante in self.get_instantes():
      for maquina in self.cronograma.get_maquinas():
        # Se obtienen solo las tareas que pertencen a la máquina iterada
        for tarea in maquina.get_tareas():
          for pedido in self.cronograma.get_pedidos():
            for producto in pedido.get_productos_maquina_tarea(maquina,tarea):
              if self.is_instante_maquina_tarea_producto_pedido[
                instante][maquina.id][tarea.id][producto.id][pedido.id].value() == 1:
                self.cronograma.add_intervalo(instante,maquina,tarea,pedido,producto,
                  self.cantidad_tarea_en_instante[tarea.id][producto.id][pedido.id][instante].value())

  def planificar(self):
    
    self.resolver_modelo_busqueda_secuencial()

    if not self.is_modelo_resuelto():
      raise ModeloLinealNoResuelto(_(u'No a podido resolverse el modelo lineal.'))

    self.completar_cronograma()
    

