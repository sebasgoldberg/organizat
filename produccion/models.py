# coding=utf-8
from django.db import models
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

class Maquina(models.Model):
  descripcion = models.CharField(max_length=100, verbose_name=_(u'Descripción'), unique=True)

  class Meta:
    ordering = ['descripcion']
    verbose_name = _(u"Maquina")
    verbose_name_plural = _(u"Maquinas")

class Tarea(models.Model):
  descripcion = models.CharField(max_length=100, verbose_name=_(u'Descripción'), unique=True)
  tiempo = models.DecimalField(
    max_digits=7, decimal_places=2, verbose_name=_(u'Tiempo (min)'), 
    help_text=_(u'Tiempo necesario para realizar la tarea por unidad de producto.'))
  class Meta:
    ordering = ['descripcion']
    verbose_name = _(u"Tarea")
    verbose_name_plural = _(u"Tareas")

class TareaMaquina(models.Model):
  """
  Tareas que puede realizar una máquina.
  """
  maquina = models.ForeignKey(Maquina, verbose_name=_(u'Maquina'))
  tarea = models.ForeignKey(Tarea, verbose_name=_(u'Tarea'))

  class Meta:
    ordering = ['maquina__descripcion','tarea__descripcion']
    verbose_name = _(u"Tarea de una máquina")
    verbose_name_plural = _(u"Tareas por máquinas")
    unique_together = (('maquina', 'tarea'),)

  def __unicode__(self):
    return _(u'%(tarea)s en máquina %(maquina)s') % {
      'tarea': self.tarea.descripcion,
      'maquina': self.maquina.descripcion,}

class Producto(models.Model):
  descripcion = models.CharField(max_length=100, verbose_name=_(u'Descripción'), unique=True)

  class Meta:
    ordering = ['descripcion']
    verbose_name = _(u"Producto")
    verbose_name_plural = _(u"Productos")

class TareaProducto(models.Model):
  """
  Tareas por las que se compone un producto
  """
  producto = models.ForeignKey(Producto, verbose_name=_(u'Producto'))
  tarea = models.ForeignKey(Tarea, verbose_name=_(u'Tarea'))
  
  class Meta:
    ordering = ['producto__descripcion', 'tarea__descripcion',]
    verbose_name = _(u"Tarea a realizar en producto")
    verbose_name_plural = _(u"Tareas por productos")
    unique_together = (('producto', 'tarea'),)

class TiempoRealizacionTarea(models.Model):
  """
  Se completa en forma automática en función de:
  - Las tareas posibles que puede tener una máquina.
  - Las tareas necesarias para realizar un producto.
  El tiempo predeterminado es el tiempo de la tarea indicada.
  """
  maquina = models.ForeignKey(Maquina, verbose_name=_(u'Maquina'), editable=False)
  producto = models.ForeignKey(Producto, verbose_name=_(u'Producto'), editable=False)
  tarea = models.ForeignKey(Tarea, verbose_name=_(u'Tarea'), editable=False)
  tiempo = models.DecimalField(
    max_digits=7, decimal_places=2, verbose_name=_(u'Tiempo (min)'), 
    help_text=_(u'Tiempo para realizar la tarea en la máquina y producto indicados, por unidad de producto.'))
  activa = models.BooleanField(default=True, verbose_name=(u'Activa'),
    help_text=_(u'Indica si la tarea se puede realizar en la máquina para el producto dado.'))
  
  class Meta:
    ordering = ['maquina__descripcion', 'producto__descripcion', 'tarea__descripcion',]
    verbose_name = _(u"Tiempo de producción")
    verbose_name_plural = _(u"Tiempos de producción")
    unique_together = (('maquina', 'producto', 'tarea'),)

class DependenciaTareaProducto(models.Model):
  """
  Indica precedencia entre tareas.
  Validar:
    - Las tareas no pueden ser la misma tarea.
    - No puede haber referencia circular.
  """
  producto = models.ForeignKey(Producto, verbose_name=_(u'Tarea en máquina'))
  tarea = models.ForeignKey(Tarea, verbose_name=_(u'La tarea'), 
    related_name='mis_dependencias', on_delete=models.PROTECT)
  tarea_anterior = models.ForeignKey(Tarea, verbose_name=_(u'Depende de la tarea'),
    help_text=_(u'Esta tarea debe realizarse antes'),
    related_name='dependientes_de_mi', on_delete=models.PROTECT)

  class Meta:
    ordering = ['producto__descripcion','tarea__descripcion','tarea_anterior__descripcion']
    verbose_name = _(u"Dependencia de tareas en producto")
    verbose_name_plural = _(u"Dependencias de tareas en productos")
    unique_together = (('producto', 'tarea', 'tarea_anterior'),)

  def clean(self):
    if self.tarea and self.tarea_anterior:

      if self.tarea.id == self.tarea_anterior.id:
        raise ValidationError(_(u'Las tareas seleccionadas deben diferir'))

      if self.producto:
        self.validar_dependencia_circular(self.tarea_anterior, 
          self.tarea, self.tarea_anterior.descripcion)
    
    self.validar_tarea_corresponde_producto(self.tarea)
    self.validar_tarea_corresponde_producto(self.tarea_anterior)

  def validar_tarea_corresponde_producto(self,tarea):
    if self.producto and tarea:
      try:
        TareaProducto.objects.get(producto=self.producto,tarea=tarea)
      except TareaProducto.DoesNotExist:
        raise ValidationError(_(u'La tarea %s no forma parte del proceso de producción del producto %s.') % (
          tarea.descripcion, self.producto.descripcion))

  def validar_dependencia_circular(self, tarea_inicial, tarea_anterior, camino):
    dependencias = DependenciaTareaProducto.objects.filter(
      producto=self.producto, tarea_anterior=tarea_anterior)
    for dependencia in dependencias:
      nuevo_camino = '%s -> %s' % (camino, dependencia.tarea_anterior.descripcion)
      if tarea_inicial.id == dependencia.tarea.id:
        nuevo_camino = '%s -> %s' % (nuevo_camino, dependencia.tarea.descripcion)
        raise ValidationError(_(u'Dependencia circular detectada: %s') % nuevo_camino)
      self.validar_dependencia_circular(tarea_inicial,
        dependencia.tarea, nuevo_camino)


class Pedido(models.Model):
  descripcion = models.CharField(max_length=100, verbose_name=_(u'Descripción'))
  fecha_entrega = models.DateField(
    verbose_name=_(u'Fecha de entrega'), null=True, blank=True,
    help_text=_(u'Sea cuidadoso con colocar una fecha muy temprana, ya que sino al planificar, muy probablemente no se pueda respetar.'))

  def __unicode__(self):
    return u'#%s - %s' % (self.id, self.descripcion)

  class Meta:
    ordering = ['-id']
    verbose_name = _(u"Pedido")
    verbose_name_plural = _(u"Pedidos")

class ItemPedido(models.Model):
  """
  Item de un pedido.
  Validar:
    - No se puede repetir el producto en 2 items distintos de un mismo pedido.
  """
  pedido = models.ForeignKey(Pedido, verbose_name=_(u'Pedido'))
  producto = models.ForeignKey(Producto, verbose_name=_(u'Producto'), on_delete=models.PROTECT)
  cantidad = models.DecimalField(
    max_digits=7, decimal_places=2, verbose_name=_(u'Cantidad'))

  class Meta:
    ordering = ['-pedido__id','producto__descripcion']
    verbose_name = _(u"Item pedido")
    verbose_name_plural = _(u"Items pedidos")
    unique_together = (('pedido', 'producto',),)


from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from produccion.models import *

def agregar_combinaciones_tiempos(sender, instance, **kwargs):
  """
  Una misma tarea T que este asociada a una maquina M por un lado y a un 
  producto P por el otro debe generar una entrada (T,M,P)
  """
  tarea = instance.tarea

  for tareaMaquina in tarea.tareamaquina_set.all():
    for tareaProducto in tarea.tareaproducto_set.all():
      maquina=tareaMaquina.maquina
      producto=tareaProducto.producto
      try:
        TiempoRealizacionTarea.objects.get(tarea=tarea,
          maquina=maquina, producto=producto)
      except TiempoRealizacionTarea.DoesNotExist:
        TiempoRealizacionTarea.objects.create(tarea=tarea,
          maquina=maquina, producto=producto, tiempo=tarea.tiempo)

post_save.connect(agregar_combinaciones_tiempos, 
  sender=TareaMaquina)
post_save.connect(agregar_combinaciones_tiempos, 
  sender=TareaProducto)

def eliminar_combinaciones_tiempos_tarea_maquina(sender, instance, **kwargs):
  """
  Se eliminan todas las combinaciones asociadas al par (tarea,maquina)
  pasado.
  """
  tarea = instance.tarea
  maquina = instance.maquina
  TiempoRealizacionTarea.objects.filter(tarea=tarea, maquina=maquina).delete()

#@todo Verificar si este requisito en realidad ya no se cumple con
# on_delete = models.CASCADE (comportamiento por defecto)
post_delete.connect(eliminar_combinaciones_tiempos_tarea_maquina, 
  sender=TareaMaquina)


def eliminar_combinaciones_tiempos_tarea_producto(sender, instance, **kwargs):
  """
  Se eliminan todas las combinaciones asociadas al par (tarea,maquina)
  pasado.
  """
  tarea = instance.tarea
  producto = instance.producto
  TiempoRealizacionTarea.objects.filter(tarea=tarea, producto=producto).delete()

#@todo Verificar si este requisito en realidad ya no se cumple con
# on_delete = models.CASCADE (comportamiento por defecto)
post_delete.connect(eliminar_combinaciones_tiempos_tarea_producto, 
  sender=TareaProducto)
