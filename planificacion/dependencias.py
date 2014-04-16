# coding=utf-8
from django.utils.translation import ugettext as _
import planificacion.models
from django.core.exceptions import ValidationError

class GerenciadorDependencias:

  @staticmethod
  def crear_desde_instante(instante):
    return GerenciadorDependencias(instante.cronograma,instante.producto,instante.pedido)

  def __init__(self, cronograma, producto, pedido):
    self.cronograma = cronograma
    self.producto = producto
    self.pedido = pedido

  def verificar_agregar_instante(self, instante):
    if instante.id is not None:
      raise Exception(_(u'El instante %s ya se encuentra persistido.') % instante.id )
    if self.cronograma.id <> instante.cronograma.id or\
      self.producto.id <> instante.producto.id or\
      self.pedido.id <> instante.pedido.id:
      raise Exception(_(u'No coinciden cronograma, producto y pedido entre el gerenciador de dependencias y el instante pasado.'))
    for tarea_anterior in instante.tarea.get_anteriores(instante.producto):
      self.validar_dependencias(tarea_anterior,instante.tarea,instante_agregado=instante)

  def verificar_eliminar_instante(self, instante):
    if instante.id is None:
      raise Exception(_(u'El instante %s no se encuentra persistido.') % instante.id )
    if self.cronograma <> instante.cronograma or\
      self.producto <> instante.producto or\
      self.pedido <> instante.pedido:
      raise Exception(_(u'No coinciden cronograma, producto y pedido entre el gerenciador de dependencias y el instante pasado.'))
    for tarea_posterior in instante.tarea.get_posteriores(instante.producto):
      self.validar_dependencias(instante.tarea, tarea_posterior, instante_borrado=instante)

  def verificar_modificar_instante(self, instante):
    if instante.id is None:
      raise Exception(_(u'El instante %s no se encuentra persistido.') % instante.id )
    if self.cronograma <> instante.cronograma or\
      self.producto <> instante.producto or\
      self.pedido <> instante.pedido:
      raise Exception(_(u'No coinciden cronograma, producto y pedido entre el gerenciador de dependencias y el instante pasado.'))
    for tarea_anterior in instante.tarea.get_anteriores(instante.producto):
      self.validar_dependencias(tarea_anterior, instante.tarea, instante_modificado=instante)
    for tarea_posterior in instante.tarea.get_posteriores(instante.producto):
      self.validar_dependencias(instante.tarea, tarea_posterior, instante_modificado=instante)

  def get_intervalos(self, tareas, instante_agregado=None, instante_borrado=None, instante_modificado=None):
    intervalos_set = planificacion.models.IntervaloCronograma.objects
    if instante_borrado:
      intervalos_set = intervalos_set.exclude(id=instante_borrado.id)
    if instante_modificado:
      intervalos_set = intervalos_set.exclude(id=instante_modificado.id)
    intervalos = [ i for i in intervalos_set.filter(
      cronograma=self.cronograma,
      producto=self.producto,
      pedido=self.pedido,
      tarea__in=tareas) ]
    if instante_modificado:
      intervalos.append(instante_modificado)
    if instante_agregado:
      intervalos.append(instante_agregado)
    return intervalos

  def get_particion_ordenada_temporal(self, intervalos, tiempos_a_incluir=[]):
    particion = []
    for intervalo in intervalos:
      particion.append(intervalo.get_fecha_desde())
      particion.append(intervalo.get_fecha_hasta())
    particion = list(set(particion)) + tiempos_a_incluir
    particion.sort()
    return particion

  def get_intervalos_anteriores(self, intervalos, tarea, fecha):
    result = []
    for intervalo in intervalos:
      if intervalo.tarea.id == tarea.id and\
        intervalo.get_fecha_desde() <= fecha:
        result.append(intervalo)
    return result

  def get_cantidad_tarea_hasta(self, intervalos, tarea, fecha):
    cantidad_tarea = 0
    for intervalo in self.get_intervalos_anteriores(intervalos, tarea, fecha):
      if intervalo.get_fecha_hasta() <= fecha:
        tiempo = intervalo.tiempo_intervalo * 60
      else:
        tiempo = (fecha - intervalo.fecha_desde).seconds 
      cantidad_tarea += tiempo / float(intervalo.get_tiempo_tarea() * 60)
    return cantidad_tarea

  def validar_dependencias(self, tarea_anterior, tarea_posterior, instante_agregado=None, instante_borrado=None, instante_modificado=None):
    operaciones = 0
    if instante_agregado: operaciones+=1
    if instante_borrado: operaciones+=1
    if instante_modificado: operaciones+=1
    if operaciones <> 1:
      raise Exception('Solo puede informar una única operación por instante')

    intervalos=self.get_intervalos([tarea_anterior, tarea_posterior], instante_agregado, instante_borrado, instante_modificado)
    particion_temporal = self.get_particion_ordenada_temporal(intervalos)
    for t in particion_temporal:
      cantidad_tarea_posterior = self.get_cantidad_tarea_hasta(intervalos, tarea_posterior, t)
      cantidad_tarea_anterior = self.get_cantidad_tarea_hasta(intervalos, tarea_anterior, t)
      if cantidad_tarea_posterior > cantidad_tarea_anterior:
        raise ValidationError(
          "La cantidad %s de tarea %s es mayor que la cantidad %s de la tarea %s de la cual depende en el instante %s" %\
          (cantidad_tarea_posterior, tarea_posterior.descripcion, cantidad_tarea_anterior, tarea_anterior.descripcion, t) )

  def crear_intervalo(self, maquina, tarea, fecha_desde, tiempo_intervalo):
    intervalo =\
      planificacion.models.IntervaloCronograma(cronograma=self.cronograma, maquina=maquina, tarea=tarea,
      producto=self.producto, pedido=self.pedido, fecha_desde=fecha_desde, 
      tiempo_intervalo=tiempo_intervalo)
    intervalo.clean()
    intervalo.save()
    return intervalo

  def crear_intervalo_al_final(self, maquina, tarea, tiempo):
    tareas = tarea.get_anteriores(self.producto)
    tareas.append(tarea)
    intervalos=self.get_intervalos(tareas)
    ultima_fecha_maquina = self.cronograma.get_ultima_fecha(maquina)
    particion_temporal = self.get_particion_ordenada_temporal(intervalos, [ultima_fecha_maquina])
    if len(particion_temporal) == 0:
      particion_temporal.append(self.cronograma.fecha_inicio)
    intervalo =\
      planificacion.models.IntervaloCronograma(cronograma=self.cronograma, maquina=maquina, tarea=tarea,
      producto=self.producto, pedido=self.pedido, tiempo_intervalo=tiempo)
    for t in particion_temporal:
      if t >= ultima_fecha_maquina:
        try:
          intervalo.fecha_desde = t
          intervalo.clean()
          intervalo.save()
          return intervalo
        except ValidationError:
          pass
    
    # En caso de no haber podido crear significa que toda la partición
    # temporal se encuentra antes que la ultima fecha de la máquina
    intervalo.fecha_desde = ultima_fecha_maquina
    intervalo.clean()
    intervalo.save()
    return intervalo

  def add_intervalos_to_cronograma(self, maquina, tarea, tiempo):
    huecos = self.cronograma.get_huecos(maquina)
    for hueco in huecos:
      try:
        tiempo_intervalo = min(tiempo, hueco.tiempo.seconds / 60)
        intervalo = self.crear_intervalo(maquina, tarea, hueco.fecha_desde, tiempo_intervalo)
        tiempo -= tiempo_intervalo
      except ValidationError:
        pass
      if tiempo <= 0:
        return

    self.crear_intervalo_al_final(maquina, tarea, tiempo)

