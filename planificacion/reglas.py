# coding=utf-8
from django.db.models import signals
from produccion.models import ItemPedido
from planificacion.models import IntervaloCronograma
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from cleansignal.models import clean_performed

#----------------------------------------------------------------------
# Reglas ItemPedido
#----------------------------------------------------------------------

class ItemYaPlanificado(ValidationError):
  pass

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


clean_performed.connect(validar_modificar_item_pedido,
    sender=ItemPedido)

signals.pre_delete.connect(validar_eliminar_item_pedido,
    sender=ItemPedido)
