# coding=utf-8
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import timedelta as TD
import logging
import traceback

logger = logging.getLogger(__name__)

class GerenciadorDependencias:

  @staticmethod
  def crear_desde_instante(instante):
    return GerenciadorDependencias(instante.cronograma,instante.producto,instante.pedido)

  def __init__(self, cronograma, producto, pedido):
    self.cronograma = cronograma
    self.producto = producto
    self.pedido = pedido

  def get_tolerancia(self):
    return 0.1

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

    intervalos_set = (
      self.cronograma.get_intervalos_propios_no_cancelados() |
      self.cronograma.get_intervalos_activos_otros_cronogramas() )

    intervalos_set = intervalos_set.filter(
      producto=self.producto,
      pedido=self.pedido,
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

  def get_cantidad_tarea_hasta(self, intervalos, tarea, fecha):
    cantidad_tarea = 0
    for intervalo in self.get_intervalos_anteriores(intervalos, tarea, fecha):
      if intervalo.get_fecha_hasta() <= fecha:
        tiempo = intervalo.tiempo_intervalo * 60
      else:
        tiempo = (fecha - intervalo.fecha_desde).total_seconds()
      cantidad_tarea += float(tiempo) / float(intervalo.get_tiempo_tarea() * 60)

    # Se suma la cantidad de tarea real de intervalos que ya se
    # encuentran finalizados.
    item = self.pedido.get_item_producto(self.producto)
    cantidad_realizada = item.get_cantidad_realizada(tarea)

    return float(cantidad_tarea) + float(cantidad_realizada)

  def validar_dependencias(self, tarea_anterior, tarea_posterior, instante_agregado=None, instante_borrado=None, instante_modificado=None):
    operaciones = 0
    if instante_agregado: operaciones+=1
    if instante_borrado: operaciones+=1
    if instante_modificado: operaciones+=1
    if operaciones <> 1:
      raise Exception('Solo puede informar una única operación por instante')

    intervalos_iter=self.get_intervalos([tarea_anterior, tarea_posterior], instante_agregado, instante_borrado, instante_modificado)
    intervalos = [i for i in intervalos_iter]
    logger.debug('Se validan dependencia entre las tareas %s (anterior) y %s (posterior) utilizando los siguientes intervalos:')
    logger.debug(intervalos)
    particion_temporal = self.get_particion_ordenada_temporal(intervalos)
    logger.debug('Particion temporal utilizada: %s' % particion_temporal)
    for t in particion_temporal:
      cantidad_tarea_posterior = self.get_cantidad_tarea_hasta(intervalos, tarea_posterior, t)
      cantidad_tarea_anterior = self.get_cantidad_tarea_hasta(intervalos, tarea_anterior, t)
      logger.debug('Cantidad tarea %s anterior a %s: %s' % (t, tarea_anterior, cantidad_tarea_anterior))
      logger.debug('Cantidad tarea %s posterior a %s: %s' % (t, tarea_posterior, cantidad_tarea_posterior))
      # @todo Hacer configurable la tolerancia a la diferencia de cantidad.
      if ( cantidad_tarea_posterior - cantidad_tarea_anterior ) > self.get_tolerancia():
        raise ValidationError(
          "La cantidad %s de tarea %s es mayor que la cantidad %s de la tarea %s de la cual depende en el instante %s" %\
          (cantidad_tarea_posterior, tarea_posterior.descripcion, cantidad_tarea_anterior, tarea_anterior.descripcion, t) )

  def crear_intervalo(self, maquina, tarea, fecha_desde, tiempo_intervalo, save=True):
    intervalo = self.cronograma.crear_intervalo(
      maquina=maquina, tarea=tarea, producto=self.producto,
      pedido=self.pedido, fecha_desde=fecha_desde, tiempo_intervalo=tiempo_intervalo)
    intervalo.clean()
    if save:
      intervalo.save()
    return intervalo

  def crear_intervalo_optimizado_en_hueco(self, maquina, tarea, hueco, tiempo_intervalo):

    intervalo = None

    cota_inferior = 0
    cota_superior = hueco.tiempo.total_seconds() - 1
    fecha_desde = hueco.fecha_desde

    # Se optimiza hasta la media hora
    while (cota_superior - cota_inferior > 0 ):

      incremento_temporal = int((cota_inferior + cota_superior) / 2)

      try:
        fecha_desde = hueco.fecha_desde + TD(seconds=int(incremento_temporal))
        tiempo = min(tiempo_intervalo, (hueco.get_fecha_hasta() - fecha_desde).total_seconds() / 60)
        if tiempo <> tiempo_intervalo and tiempo < self.cronograma.tiempo_minimo_intervalo:
          break
        intervalo = self.crear_intervalo(maquina, tarea, fecha_desde, tiempo, save=False)
        cota_superior = incremento_temporal - 1
      except ValidationError:
        cota_inferior = incremento_temporal + 1
    
    if intervalo is not None:
      intervalo.save()

    return intervalo

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
            ugettext_lazy((u'No se ha podido completar la planificación. '+
              u'Seguramente puede solucionar este error, aumentando la opción '+
              u'tiempo mínimo del intervalo en la configuración del cronograma.')))
        if tiempo <= 0:
          break

    assert tiempo == 0

