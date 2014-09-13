# coding=utf-8
from django.db.models import signals
from produccion.models import ItemPedido
from planificacion.models import (IntervaloCronograma, 
    MaquinaCronograma,
    PedidoCronograma,
    TareaProducto)
from calendario.models import ExcepcionLaborable
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from cleansignal.models import clean_performed

def mismos_valores_instancia(ix, iy):
  if ix.__class__ <> iy.__class__:
    raise Exception(_(u'Una instancia de la clase %s no '+
      u'puede compararse con una instancia de la clase %s.')%
      (ix.__class__, iy.__class__))

  for field in ix.__class__._meta.fields:
    # Si existe alguna diferencia entonces las instancias son
    # distintas.
    if ix.__getattribute__(field.name) <> iy.__getattribute__(field.name):
      return False
  
  return True

def is_instancia_modificada(instancia):
  if instancia.id is None:
    raise Exception(_(u'No se puede comparar una instancia sin un '+
      u'ID definido.'))
  db_instance = instancia.__class__.objects.get(pk=instancia.id)
  return not mismos_valores_instancia(instancia, db_instance)


#----------------------------------------------------------------------
# Validaciones Genéricas de Instancia
#----------------------------------------------------------------------
class InstanciaYaUtilizadaEnPlanificacion(ValidationError):
  pass

def wrapper_validar_eliminar_instancia(e):

  def validar_eliminar_instancia(sender, instance,
      *args, **kwargs):
    if instance.intervalocronograma_set.filter(
        ).exists():
      raise e 

  return validar_eliminar_instancia

def wrapper_validar_modificar_instancia(validar_eliminar_instancia):

  def validar_modificar_instancia(sender, instance,
      *args, **kwargs):

    if instance.id is None:
      return

    db_instance = instance.__class__.objects.get(pk=instance.id)

    if not mismos_valores_instancia(db_instance, instance):
      validar_eliminar_instancia(sender, db_instance,
          *args, **kwargs)

  return validar_modificar_instancia


#----------------------------------------------------------------------
# Validaciones de ItemPedido
#----------------------------------------------------------------------

class ItemYaPlanificado(ValidationError):
  pass


def validar_modificar_item_pedido(sender, instance, *args, **kwargs):

  item = instance

  if item.id is None:
    return

  if not is_instancia_modificada(item):
    return

  try:
    intervalo = IntervaloCronograma.get_intervalos_no_cancelados(
        ).filter(item=item).first()
    if intervalo is not None:
      raise ItemYaPlanificado(_(u'El item %s se encuentra '+
        u'planificado en el cronograma %s. Imposible modificar.') % (
          item, intervalo.cronograma))
  except IntervaloCronograma.DoesNotExist:
    pass


def validar_eliminar_item_pedido(sender, instance, *args, **kwargs):

  item = instance

  if item.id is None:
    return

  try:
    intervalo = IntervaloCronograma.get_intervalos_no_cancelados(
        ).filter(item=item).first()
    if intervalo is not None:
      raise ItemYaPlanificado(_(u'El item %s se encuentra '+
        u'planificado en el cronograma %s. Imposible borrar.') % (
          item, intervalo.cronograma))
  except IntervaloCronograma.DoesNotExist:
    pass


#----------------------------------------------------------------------
# Validaciones de Excepciones Laborables
#----------------------------------------------------------------------

class IntervaloCalendarioConPlanificacionExistente(ValidationError):
  pass

def existe_solapamiento_intervalos(qs_intervalos, fecha_desde, fecha_hasta):

  if qs_intervalos.filter(
    fecha_desde__lte=fecha_desde, 
    fecha_hasta__gte=fecha_hasta).exists():
    return True

  if qs_intervalos.filter(
    fecha_desde__lte=fecha_hasta, 
    fecha_hasta__gte=fecha_hasta).exists():
    return True

  if qs_intervalos.filter(
    fecha_desde__gte=fecha_desde, 
    fecha_desde__lte=fecha_hasta).exists():
    return True

  if qs_intervalos.filter(
    fecha_hasta__gte=fecha_desde, 
    fecha_hasta__lte=fecha_desde).exists():
    return True

  return False

def validar_eliminar_excepcion_laborable(sender, instance,
    *args, **kwargs):

  if instance.id is None:
    return

  excepcion = instance

  if excepcion.laborable:
    if existe_solapamiento_intervalos(
        IntervaloCronograma.get_intervalos_modificables(),
        excepcion.get_fecha_desde(),
        excepcion.get_fecha_hasta()):
      raise IntervaloCalendarioConPlanificacionExistente(
          _(u'Imposible eliminar/modificar excepción laborable '+
            u'existen planificaciones en el intervalo definido.'))
  else:
    # Toda excepción no laborable debería poder ser eliminada.
    pass
 
def validar_modificar_excepcion_laborable(sender, instance,
    *args, **kwargs):

  if instance.id is None:
    return

  excepcion = ExcepcionLaborable.objects.get(pk=instance.id)

  if mismos_valores_instancia(instance, excepcion):
    return

  validar_eliminar_excepcion_laborable(sender, excepcion,
      *args, **kwargs)

def validar_agregar_excepcion_laborable(sender, instance,
    *args, **kwargs):

  if instance.id is not None:
    if not is_instancia_modificada(instance):
      return

  excepcion = instance

  if not excepcion.laborable:
    if existe_solapamiento_intervalos(
        IntervaloCronograma.get_intervalos_modificables(),
        excepcion.get_fecha_desde(),
        excepcion.get_fecha_hasta()):
      raise IntervaloCalendarioConPlanificacionExistente(
          _(u'Imposible agregar/modificar excepción laborable '+
            u'existen planificaciones en el intervalo definido.'))
  else:
    # Toda excepción laborable debería poder ser agregada.
    pass

#----------------------------------------------------------------------
# Validaciones de Intervalos Laborables
#----------------------------------------------------------------------
# TODO Agregar validaciones

#----------------------------------------------------------------------
# Validaciones de Maquinas Cronogramas
#----------------------------------------------------------------------
class MaquinaYaUtilizadaEnPlanificacion(ValidationError):
  pass

validar_eliminar_maquina_cronograma = wrapper_validar_eliminar_instancia(
    MaquinaYaUtilizadaEnPlanificacion(_(
      u'La máquina que se intenta modificar/borrar presenta '+
      u'intervalos planificados.')))

validar_modificar_maquina_cronograma = wrapper_validar_modificar_instancia(
    validar_eliminar_maquina_cronograma)


#----------------------------------------------------------------------
# Validaciones de Pedidos Cronogramas
#----------------------------------------------------------------------
class PedidoYaUtilizadoEnPlanificacion(ValidationError):
  pass

validar_eliminar_pedido_cronograma = wrapper_validar_eliminar_instancia(
    PedidoYaUtilizadoEnPlanificacion(_(
      u'El pedido que se intenta modificar/borrar presenta '+
      u'intervalos planificados.')))

validar_modificar_pedido_cronograma = wrapper_validar_modificar_instancia(
    validar_eliminar_pedido_cronograma)

#----------------------------------------------------------------------
# Validaciones de Tarea Producto
#----------------------------------------------------------------------
class ProductoYaUtilizadoEnPlanificacion(ValidationError):
  pass

validar_eliminar_tarea_producto = wrapper_validar_eliminar_instancia(
    ProductoYaUtilizadoEnPlanificacion(_(
      u'La tarea del producto que se intenta modificar/borrar presenta '+
      u'intervalos planificados.')))

validar_modificar_tarea_producto = wrapper_validar_modificar_instancia(
    validar_eliminar_tarea_producto)

#----------------------------------------------------------------------
# Validaciones de Dependencias en Tareas
#----------------------------------------------------------------------
# TODO Agregar validaciones


#----------------------------------------------------------------------
# Conexiones a las señales
#----------------------------------------------------------------------

# ItemPedido
clean_performed.connect(validar_modificar_item_pedido,
    sender=ItemPedido)

signals.pre_delete.connect(validar_eliminar_item_pedido,
    sender=ItemPedido)


# ExcepcionLaborable
clean_performed.connect(validar_modificar_excepcion_laborable,
    ExcepcionLaborable)

clean_performed.connect(validar_agregar_excepcion_laborable,
    ExcepcionLaborable)

signals.pre_delete.connect(validar_eliminar_excepcion_laborable,
    ExcepcionLaborable)


# MaquinaCronograma
clean_performed.connect(validar_modificar_maquina_cronograma,
    MaquinaCronograma)

signals.pre_delete.connect(validar_eliminar_maquina_cronograma,
    MaquinaCronograma)


# PedidoCronograma
clean_performed.connect(validar_modificar_pedido_cronograma,
    PedidoCronograma)

signals.pre_delete.connect(validar_eliminar_pedido_cronograma,
    PedidoCronograma)


# TareaProducto
clean_performed.connect(validar_modificar_tarea_producto,
    TareaProducto)

signals.pre_delete.connect(validar_eliminar_tarea_producto,
    TareaProducto)

