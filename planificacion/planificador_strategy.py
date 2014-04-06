# coding=utf-8
from planificacion.models import Cronograma
from pulp import *

class PlanificadorStrategy:

  cronograma = None

  def __init__(self, cronograma):
    self.cronograma = cronograma
  
  def planificar(self, cronograma):
    raise Exception(_(u'Método no implementado'))
    
class PlanificadorModeloLineal(PlanificadorStrategy):

  max_instante = None
  modelo = None
  # Variables
  tiempos_maquinas = {}
  is_maximo_tiempo_maquina = {}
  is_instante_maquina_tarea_producto_pedido = {}

  def definir_variables(self):
    for maquinacronograma in cronograma.maquinacronograma_set:
      maquina = maquinacronograma.maquina
      self.tiempos_maquinas[maquina.id] = LpVariable(
        "Tiempo de máquina %s" % maquina.descripcion,0)
      self.is_maximo_tiempo_maquina[maquina.id] = LpVariable(
        "La maquina %s tiene el tiempo máximo" % maquina.descripcion,0,1,LpInteger)

    for instante in range(1,self.max_instante+1):
      for maquinacronograma in cronograma.maquinacronograma_set:
        maquina = maquinacronograma.maquina
        # Se obtienen solo las tareas que pertencen a la máquina iterada
        for tareamaquina in maquina.tareamaquina_set.all():
          tarea = tareamaquina.tarea
          for pedidocronograma in cronograma.pedidocronograma_set.all():
            pedido = pedidocronograma.pedido
            for productopedido in pedido.productopedido_set.all():
              producto = productopedido.producto
              try:
                # Se usan solo las tareas que componen al producto iterado
                TareaProducto.get(producto=producto,tarea=tarea)
                is_instante_maquina_tarea_producto_pedido[
                  instante][maquina.id][tarea.id][producto.id][pedido.id] = LpVariable(
                    "El instante %s se utiliza en la máquina %s para ejecutar la \
                    tarea %s para fabricar el producto %s del pedido %s." % \
                    (instante, maquina.descripcion, tarea.descripcion, pedido.descripcion,
                    producto.descripcion),0,1,LpInteger)
              except TareaProducto.DoesNotExist:
                pass

  def definir_modelo(self):
    """
    @todo Ver: https://pythonhosted.org/PuLP/CaseStudies/a_sudoku_problem.html
    """
    # Creamos el modelo e indicamos que se trata de un problema de búsqueda de mínimo
    self.modelo = LpProblem(cronograma.descripcion,LpMinimize)
    tiempo_produccion=LpVariable("Tiempo de producción",0)
    # Creamos la función objetivo
    self.modelo += tiempo_produccion, "Tiempo total de producción"
    # Definimos el tiempo de cada máquina
    self.definir_variables()
    # obtención del máximo
    self.definir_restricciones()
