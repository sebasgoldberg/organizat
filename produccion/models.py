# coding=utf-8
from django.db import models
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

class TareaAnteriorNoExiste(Exception):
  pass

class Maquina(models.Model):
  descripcion = models.CharField(max_length=100, verbose_name=_(u'Descripción'), unique=True)

  class Meta:
    ordering = ['descripcion']
    verbose_name = _(u"Maquina")
    verbose_name_plural = _(u"Maquinas")

  def __unicode__(self):
    return self.descripcion

  def get_tareas_pedidos(self, pedidos):
    tareas = set()
    for pedido in pedidos:
      for producto in pedido.get_productos():
        for tarea in producto.get_tareas_maquina(self):
          tareas.add(tarea)
    return tareas

  def get_tareas(self):
    return [ x.tarea for x in self.tareamaquina_set.all() ]

  def add_tarea(self,tarea):
    tm=TareaMaquina(tarea=tarea,maquina=self)
    tm.clean()
    tm.save()
    return tm

class Tarea(models.Model):
  descripcion = models.CharField(max_length=100, verbose_name=_(u'Descripción'), unique=True)
  tiempo = models.DecimalField(
    max_digits=7, decimal_places=2, verbose_name=_(u'Tiempo (min)'), 
    help_text=_(u'Tiempo necesario para realizar la tarea por unidad de producto.'))
  class Meta:
    ordering = ['descripcion']
    verbose_name = _(u"Tarea")
    verbose_name_plural = _(u"Tareas")

  def __unicode__(self):
    return self.descripcion

  def get_maquinas(self):
    return [ x.maquina for x in self.tareamaquina_set.all() ]

  def get_maquinas_producto(self, producto):
    return [ t.maquina for t in self.tiemporealizaciontarea_set.filter(producto=producto, activa=True) ]

  def get_tiempo(self,maquina,producto):
    return TiempoRealizacionTarea.objects.get(tarea=self,
      maquina=maquina, producto=producto, activa=True).tiempo
  
  def get_tiempo_maximo(self, producto):
    tiempo_tarea_por_producto = self.tiemporealizaciontarea_set.filter(producto=producto, activa=True)
    if tiempo_tarea_por_producto.count() == 0:
      raise TiempoTareaNoEncontrado(_u('No se ha encontrado tiempo para la tarea %s, producto %s') %\
        (self.id, producto.id))
    return tiempo_tarea_por_producto.aggregate(models.Max('tiempo'))['tiempo__max']

  def get_cantidad_producir(self, producto, pedido):
    item = pedido.get_item_producto(producto)
    return item.cantidad

  def has_tareas_anteriores(self, producto):
    return len(DependenciaTareaProducto.objects.filter(producto=producto,tarea=self)) > 0

  def get_anteriores(self, producto):
    return [ d.tarea_anterior for d in DependenciaTareaProducto.objects.filter(tarea=self,producto=producto) ]

  def get_posteriores(self, producto):
    return [ d.tarea for d in DependenciaTareaProducto.objects.filter(tarea_anterior=self,producto=producto) ]

  def get_secuencias_dependencias(self, producto):
    """
    Devuelve una lista de listas.
    Cada lista contiene una secuencia de dependencias.
    """
    tareas_posteriores = self.get_posteriores(producto)
    if len(tareas_posteriores) == 0:
      return [[self]]

    result = []
    for tarea_posterior in tareas_posteriores:
      secuencias_dependencias = tarea_posterior.get_secuencias_dependencias(producto)
      for secuencia_dependencias in secuencias_dependencias:
        result.append([self]+secuencia_dependencias)

    return result

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
  descripcion = models.CharField(max_length=100, verbose_name=_(u'Descripción'), unique=True,
      null=True, blank=False)

  class Meta:
    ordering = ['descripcion']
    verbose_name = _(u"Producto")
    verbose_name_plural = _(u"Productos")

  def __unicode__(self):
    return self.descripcion

  def get_tareas(self):
    return [ x.tarea for x in self.tareaproducto_set.all() ]

  def get_tareas_maquina(self, maquina):
    return [ t.tarea for t in self.tiemporealizaciontarea_set.filter(
      maquina=maquina, activa=True) ]

  def get_maquinas_tarea(self, tarea):
    return [ t.maquina for t in self.tiemporealizaciontarea_set.filter(tarea=tarea,
      activa=True) ]

  def add_dependencia_tareas(self, tarea_anterior, tarea):
    d=DependenciaTareaProducto(producto=self,tarea_anterior=tarea_anterior,tarea=tarea)
    d.clean()
    d.save()
    return d

  def get_tareas_primer_grado_dependencia(self):
    
    tareas_anteriores = [d.tarea_anterior for d in DependenciaTareaProducto.objects.filter(producto=self)]
    primer_grado = []
    for tarea in tareas_anteriores:
      if not tarea.has_tareas_anteriores(producto=self):
        primer_grado.append(tarea)

    return primer_grado

  def get_listado_secuencias_dependencias(self):

    primer_grado = self.get_tareas_primer_grado_dependencia()
    secuencias_dependencias = []

    for tarea_primer_grado in primer_grado:
      secuencias_dependencias += tarea_primer_grado.get_secuencias_dependencias(self)

    return secuencias_dependencias

  def get_tareas_ordenadas_por_dependencia(self):

    primer_grado = self.get_tareas_primer_grado_dependencia()

    grados_tareas = {}
    for secuencia_dependencia in self.get_listado_secuencias_dependencias():
      grado = 0
      for tarea in secuencia_dependencia:
        grado+=1
        if not grados_tareas.has_key(tarea.id):
          grados_tareas[tarea.id]={}
          grados_tareas[tarea.id]['tarea'] = tarea
          grados_tareas[tarea.id]['grado'] = grado
        elif grados_tareas[tarea.id]['grado'] < grado:
          grados_tareas[tarea.id]['grado'] = grado

    tareas_por_grado = {}
    for grado_tarea in grados_tareas.itervalues():
      if not tareas_por_grado.has_key(grado_tarea['grado']):
        tareas_por_grado[grado_tarea['grado']] = []
      tareas_por_grado[grado_tarea['grado']].append(grado_tarea['tarea'])

    tareas_ordenadas_por_grado_dependencia=[]
    # Se recorre diccionario en forma ordenada
    for i in range(1,len(tareas_por_grado)+1):
      tareas_ordenadas_por_grado_dependencia += tareas_por_grado[i]

    ids_tareas_dependientes = [ t.id for t in tareas_ordenadas_por_grado_dependencia]
    tareas_independientes = []
    # Se obtienen las tareas independientes:
    for tarea in self.get_tareas():
      if tarea.id not in ids_tareas_dependientes:
        tareas_independientes.append(tarea)

    return tareas_ordenadas_por_grado_dependencia +\
      tareas_independientes


class ProductoProxyDependenciasTareas(Producto):
  class Meta:
    proxy = True
    ordering = ['descripcion']
    verbose_name = _(u"Dependencia de tarea en producto")
    verbose_name_plural = _(u"Dependencias de tareas en productos")

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
  
  # aeguran el borrado en cascada en caso que la relación entre la tarea y,
  # la máquina o el producto, sea eliminada.
  tareamaquina = models.ForeignKey(TareaMaquina, editable=False)
  tareaproducto = models.ForeignKey(TareaProducto, editable=False)

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
    related_name='mis_dependencias')
  tarea_anterior = models.ForeignKey(Tarea, verbose_name=_(u'Depende de la tarea'),
    help_text=_(u'Esta tarea debe realizarse antes'),
    related_name='dependientes_de_mi')

  # campos para consistencia
  tareaproducto = models.ForeignKey(TareaProducto, editable=False,
    related_name='mis_dependencias')
  tarea_anteriorproducto = models.ForeignKey(TareaProducto, editable=False,
    related_name='dependientes_de_mi')

  class Meta:
    ordering = ['producto__descripcion','tarea__descripcion','tarea_anterior__descripcion']
    verbose_name = _(u"Dependencia de tareas en producto")
    verbose_name_plural = _(u"Dependencias de tareas en productos")
    unique_together = (('producto', 'tarea', 'tarea_anterior'),)

  def get_tarea_producto(self, tarea):
    try:
      return TareaProducto.objects.get(tarea=tarea, producto=self.producto)
    except TareaProducto.DoesNotExist:
      raise ValidationError(_(u'La tarea %s no forma parte de la producción del producto %s')%(
        tarea.descripcion,self.producto.descripcion))

  def save(self, *args, **kwargs):
    self.clean()
    super(DependenciaTareaProducto, self).save(*args, **kwargs) 

  def clean(self):
    if self.tarea and self.tarea_anterior:

      if self.tarea.id == self.tarea_anterior.id:
        raise ValidationError(_(u'Las tareas seleccionadas deben diferir'))

      if self.producto:
        self.validar_dependencia_circular([self.tarea_anterior.id], 
          self.tarea, self.tarea_anterior.descripcion)

        self.tareaproducto = self.get_tarea_producto(tarea=self.tarea)
        self.tarea_anteriorproducto = self.get_tarea_producto(tarea=self.tarea_anterior)

    self.validar_tarea_corresponde_producto(self.tarea)
    self.validar_tarea_corresponde_producto(self.tarea_anterior)

  def validar_tarea_corresponde_producto(self,tarea):
    if self.producto and tarea:
      try:
        TareaProducto.objects.get(producto=self.producto,tarea=tarea)
      except TareaProducto.DoesNotExist:
        raise ValidationError(_(u'La tarea %s no forma parte del proceso de producción del producto %s.') % (
          tarea.descripcion, self.producto.descripcion))

  def validar_dependencia_circular(self, visitadas, tarea_anterior, camino):
    dependencias = DependenciaTareaProducto.objects.filter(
      producto=self.producto, tarea_anterior=tarea_anterior)
    for dependencia in dependencias:
      nuevo_camino = '%s -> %s' % (camino, dependencia.tarea_anterior.descripcion)
      if dependencia.tarea.id in visitadas:
        nuevo_camino = '%s -> %s' % (nuevo_camino, dependencia.tarea.descripcion)
        raise ValidationError(_(u'Dependencia circular detectada: %s') % nuevo_camino)
      visitadas.append(tarea_anterior.id)
      self.validar_dependencia_circular(visitadas,
        dependencia.tarea, nuevo_camino)

class Pedido(models.Model):
  descripcion = models.CharField(max_length=100, verbose_name=_(u'Descripción'),
      null=True, blank=False)

  def __unicode__(self):
    return u'#%s - %s' % (self.id, self.descripcion)

  class Meta:
    ordering = ['-id']
    verbose_name = _(u"Pedido")
    verbose_name_plural = _(u"Pedidos")

  def get_maquinas_posibles_produccion(self):
    maquinas = set()
    for producto in self.get_productos():
      for tarea in producto.get_tareas():
        maquinas = maquinas | set(tarea.get_maquinas())
    return maquinas

  def add_item(self, producto, cantidad):
    return self.itempedido_set.create(producto=producto,cantidad=cantidad)

  def get_items(self):
    return self.itempedido_set.all()

  def get_productos(self):
    return [ i.producto for i in self.itempedido_set.all() ]

  def get_productos_maquina_tarea(self, maquina, tarea):
    productos_pedido = [ i.producto for i in self.itempedido_set.all() ]
    for t in TiempoRealizacionTarea.objects.filter(
        producto__in=productos_pedido, maquina=maquina, tarea=tarea):
      yield t.producto

  def get_items_maquina_tarea(self, maquina, tarea):
    productos = [ p for p in self.get_productos_maquina_tarea(
      maquina, tarea) ]
    for item in self.itempedido_set.filter(producto__in=productos):
      yield item

  def get_item_producto(self, producto):
    return self.itempedido_set.get(producto=producto)

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

  def __unicode__(self):
    return _(u'P#%(pedido)s-I#%(item)s-%(producto)s') % {
        'pedido': self.pedido.id,
        'item': self.id,
        'producto': self.producto,
        }

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

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
          maquina=maquina, producto=producto, tiempo=tarea.tiempo,
          tareamaquina=tareaMaquina, tareaproducto=tareaProducto)

post_save.connect(agregar_combinaciones_tiempos, 
  sender=TareaMaquina)
post_save.connect(agregar_combinaciones_tiempos, 
  sender=TareaProducto)
