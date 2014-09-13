# coding=utf-8
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import timedelta as TD
import logging
import traceback
from decimal import Decimal as D

logger = logging.getLogger(__name__)

class GerenciadorDependencias:

  @staticmethod
  def crear_desde_instante(instante):
    return GerenciadorDependencias(instante.cronograma,instante.item)

  def __init__(self, cronograma, item):
    self.cronograma = cronograma
    self.item = item

  def get_tolerancia(self, cantidad=None):
    if cantidad is None:
      cantidad = self.item.cantidad
    return self.cronograma.get_tolerancia(cantidad)

  #@profile
  def verificar_agregar_instante(self, instante):
    if instante.id is not None:
      raise Exception(_(u'El instante %s ya se encuentra persistido.') % instante.id )
    if self.cronograma.id <> instante.cronograma.id or\
      self.item.id <> instante.item.id:
      raise Exception(_(u'No coinciden cronograma, producto y pedido entre el gerenciador de dependencias y el instante pasado.'))
    for tarea_anterior in instante.tarea.get_anteriores(instante.item.producto):
      self.validar_dependencias(tarea_anterior,instante.tarea,instante_agregado=instante)
    # TODO Verificar si es correcto no validar dependencias de tareas posteriores.

  def verificar_eliminar_instante(self, instante):
    if instante.id is None:
      raise Exception(_(u'El instante %s no se encuentra persistido.') % instante.id )
    if self.cronograma <> instante.cronograma or\
      self.item.id <> instante.item.id:
      raise Exception(_(u'No coinciden cronograma, producto y pedido entre el gerenciador de dependencias y el instante pasado.'))
    for tarea_posterior in instante.tarea.get_posteriores(instante.item.producto):
      self.validar_dependencias(instante.tarea, tarea_posterior, instante_borrado=instante)

  def verificar_modificar_instante(self, instante):
    if instante.id is None:
      raise Exception(_(u'El instante %s no se encuentra persistido.') % instante.id )
    if self.cronograma <> instante.cronograma or\
      self.item <> instante.item:
      raise Exception(_(u'No coinciden cronograma, producto y pedido entre el gerenciador de dependencias y el instante pasado.'))
    for tarea_anterior in instante.tarea.get_anteriores(instante.getItem().producto):
      self.validar_dependencias(tarea_anterior, instante.tarea, instante_modificado=instante)
    for tarea_posterior in instante.tarea.get_posteriores(instante.getItem().producto):
      self.validar_dependencias(instante.tarea, tarea_posterior, instante_modificado=instante)

  def get_intervalos(self, tareas, instante_agregado=None, instante_borrado=None, instante_modificado=None):

    intervalos_set = (
      self.cronograma.get_intervalos_propios_no_cancelados() |
      self.cronograma.get_intervalos_activos_otros_cronogramas() )

    intervalos_set = intervalos_set.filter(
      item=self.item,
      tarea__in=tareas)

    if instante_borrado:
      intervalos_set = intervalos_set.exclude(id=instante_borrado.id)
    if instante_modificado:
      intervalos_set = intervalos_set.exclude(id=instante_modificado.id)

    for i in intervalos_set:
      yield i

    if instante_modificado:
      if not instante_modificado.is_cancelado():
        yield instante_modificado

    if instante_agregado:
      yield instante_agregado

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

  #@profile
  def get_cantidad_tarea_hasta(self, intervalos, tarea, fecha):
    cantidad_tarea = 0
    for intervalo in self.get_intervalos_anteriores(intervalos, tarea, fecha):
      if intervalo.get_fecha_hasta() <= fecha:
        cantidad_tarea += D(intervalo.cantidad_tarea)
      else:
        tiempo = (fecha - intervalo.fecha_desde).total_seconds()
        cantidad_tarea += D(tiempo) / D(intervalo.get_tiempo_tarea() * 60)

    # Se suma la cantidad de tarea real de intervalos que ya se
    # encuentran finalizados.
    cantidad_realizada = self.item.get_cantidad_realizada(tarea)

    return D(cantidad_tarea) + D(cantidad_realizada)

  #@profile
  def validar_dependencias(self, tarea_anterior, tarea_posterior, instante_agregado=None, instante_borrado=None, instante_modificado=None):
    operaciones = 0
    if instante_agregado: operaciones+=1
    if instante_borrado: operaciones+=1
    if instante_modificado: operaciones+=1

    if operaciones <> 1:
      raise Exception('Solo puede informar una única operación por instante')

    intervalos_iter=self.get_intervalos([tarea_anterior, tarea_posterior], instante_agregado, instante_borrado, instante_modificado)

    intervalos = []
    fecha_inicio_tarea_posterior = None
    for i in intervalos_iter:
      if i.tarea.id == tarea_posterior.id:
        if fecha_inicio_tarea_posterior is None:
          fecha_inicio_tarea_posterior = i.fecha_desde
        else:
          fecha_inicio_tarea_posterior = min(
              fecha_inicio_tarea_posterior,
              i.fecha_desde)
      intervalos.append(i)

    logger.debug('Se validan dependencia entre las tareas %s (anterior) y %s (posterior) utilizando los siguientes intervalos:' % (
      tarea_anterior, tarea_posterior))
    logger.debug(intervalos)
    particion_temporal = self.get_particion_ordenada_temporal(intervalos)
    logger.debug('Particion temporal utilizada: %s' % particion_temporal)
    cantidad_tarea_anterior_maxima = False
    for t in particion_temporal:
      cantidad_tarea_posterior = self.get_cantidad_tarea_hasta(intervalos, tarea_posterior, t)
      cantidad_tarea_anterior = self.get_cantidad_tarea_hasta(intervalos, tarea_anterior, t)
      logger.debug('Cantidad tarea anterior %s hasta %s: %s' % (tarea_anterior, t, cantidad_tarea_anterior))
      logger.debug('Cantidad tarea posterior %s hasta %s: %s' % (tarea_posterior, t, cantidad_tarea_posterior))

      if fecha_inicio_tarea_posterior is None:
        pass
      elif t < fecha_inicio_tarea_posterior:
        pass
      elif (abs(D(self.item.cantidad) - cantidad_tarea_anterior) > 
          self.get_tolerancia()) and not cantidad_tarea_anterior_maxima:
        cantidad_tarea_anterior = (
            cantidad_tarea_anterior - 
            self.cronograma.cantidad_extra_tarea_anterior)

      if (abs(D(self.item.cantidad) - cantidad_tarea_anterior) <
          self.get_tolerancia()) and not cantidad_tarea_anterior_maxima:
        cantidad_tarea_anterior_maxima = True
        cantidad_tarea_anterior = (
            cantidad_tarea_anterior - 
            self.cronograma.cantidad_extra_tarea_anterior)

      if D(cantidad_tarea_posterior) > D(cantidad_tarea_anterior):
        if abs( cantidad_tarea_posterior - D(self.item.cantidad) ) > self.get_tolerancia():
          if cantidad_tarea_posterior - cantidad_tarea_anterior > self.get_tolerancia(cantidad_tarea_anterior):
            e = ValidationError(
              "La cantidad %s de tarea %s es mayor que la cantidad %s de la tarea %s de la cual depende en el instante %s" %\
              (cantidad_tarea_posterior, tarea_posterior.descripcion, cantidad_tarea_anterior, tarea_anterior.descripcion, t) )
            logger.debug(e)
            raise e

  #@profile
  def crear_intervalo(self, maquina, tarea, fecha_desde, tiempo_intervalo, save=True):
    intervalo = self.cronograma.crear_intervalo(
      maquina=maquina, tarea=tarea, item=self.item,
      fecha_desde=fecha_desde, tiempo_intervalo=tiempo_intervalo)
    intervalo.clean()
    if save:
      intervalo.save()
    return intervalo

  def crear_intervalo_optimizado_en_hueco(self, maquina, tarea, hueco, tiempo_intervalo):

    intervalo = None

    cota_inferior = 0
    cota_superior = hueco.tiempo.total_seconds() - 1
    fecha_desde = hueco.fecha_desde

    logger.debug('Optimizacion en hueco: %s' % hueco.__unicode__())
    # Se optimiza hasta la media hora
    while (cota_superior - cota_inferior > 0 ):

      incremento_temporal = int((cota_inferior + cota_superior) / 2)

      try:
        fecha_desde = hueco.fecha_desde + TD(seconds=int(incremento_temporal))
        logger.debug('Fecha desde: %s' % fecha_desde)
        tiempo = min(tiempo_intervalo, (hueco.get_fecha_hasta() - fecha_desde).total_seconds() / 60)
        if tiempo <> tiempo_intervalo and tiempo < self.cronograma.tiempo_minimo_intervalo:
          break
        intervalo = self.crear_intervalo(maquina, tarea, fecha_desde, tiempo, save=False)
        cota_superior = incremento_temporal - 1
      except ValidationError:
        cota_inferior = incremento_temporal + 1

    if intervalo is not None:
      try:
        intervalo.clean()
      except:
        assert False
      intervalo.save()

    return intervalo

  #@profile
  def add_intervalos_to_cronograma(self, maquina, tarea, tiempo):

    while tiempo > 0:
      for hueco in self.cronograma.get_huecos(maquina):
        logger.debug(_('Se intenta agregar en hueco %s.') % hueco.__unicode__())
        tiempo_intervalo = min(tiempo, hueco.tiempo.total_seconds() / 60)
        if tiempo_intervalo <> tiempo and tiempo_intervalo < self.cronograma.tiempo_minimo_intervalo:
          continue
        logger.debug(_('Se intenta asignar la siguiente cantidad de tiempo: %s.') % tiempo_intervalo)
        intervalo = None
        try:
          intervalo = self.crear_intervalo(maquina, tarea, hueco.fecha_desde, tiempo_intervalo)
          logger.debug(_('Se ha creado en forma exitosa el intervalo %s.') % intervalo)
        except ValidationError:
          logger.debug(traceback.format_exc())
          if self.cronograma.optimizar_planificacion:
            intervalo = self.crear_intervalo_optimizado_en_hueco(maquina, tarea, hueco, tiempo_intervalo)
        if intervalo is not None:
          logger.info(_('Intervalo agregado a cronograma %s:\n\t%s') % (
            self.cronograma, intervalo))
          tiempo = tiempo - intervalo.tiempo_intervalo
        elif ( tiempo_intervalo > 0 and
          self.cronograma.get_intervalos_propios_y_activos().filter(
            fecha_hasta__gt=hueco.fecha_desde).count() == 0 ):
          raise ValidationError(
            ugettext_lazy((u'No se ha podido completar la planificación para el item %s. '+
              u'Seguramente puede solucionar este error, aumentando la opción '+
              u'tiempo mínimo del intervalo en la configuración del cronograma.')) % self.item)
        if tiempo <= 0:
          break

    assert tiempo == 0

