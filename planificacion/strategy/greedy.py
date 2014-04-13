from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from math import ceil
from planificacion.strategy.base import PlanificadorStrategy
from planificacion.strategy.utils import add_keys_to_dict

class PlanificadorGreedy(PlanificadorStrategy):

  def distribuir_intervalos(self, intervalos):

    if len(intervalos) == 0:
      return
    
    intervalos_pendientes = []

    for intervalo in intervalos:

      try:

        intervalo_disponible = self.cronograma.get_primer_intervalo_disponible(intervalo.producto,intervalo.tarea)

        while (intervalo_disponible):

          intervalo_disponible.producto = intervalo.producto
          intervalo_disponible.tarea = intervalo.tarea
          intervalo_disponible.pedido = intervalo.pedido

          try:
            intervalo_disponible.clean()
            intervalo_disponible.save()
            break
          except ValidationError:
            pass

          intervalo_disponible = self.cronograma.get_proximo_intervalo_disponible(intervalo.producto,intervalo.tarea)

      except IntervaloDisponibleDoesNotExist:
        
        intervalos_pendientes.append(intervalo)

    self.distribuir_intervalos(intervalos_pendientes)

  def get_intervalos_a_distribuir(self, pedido):
    for item in pedido.get_items():
      for tarea in 


  def planificar(self):
    """
    La idea es:
    1) Tomar la cantidad de horas a realizar en cada tarea.
    2) Obtener las maquinas posibles para la tarea y cronograma dados.
    3) Buscar la máquina con intervalo más bajo y verificar si 
      se respetan las restricciones.
    """
    maquinas_cronograma = self.cronograma.get_maquinas()

    # Para cada pedido...
    for pedido in self.cronograma.get_pedidos():
      # Obtenemos los los intervalos de cada tarea a distribuir
      intervalos = self.get_intervalos_a_distribuir(pedido)

      self.distribuir_intervalos(intervalos)


