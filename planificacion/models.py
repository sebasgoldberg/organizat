# coding=utf-8
from django.db import models
from produccion.models import *
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from planificacion.strategy.hago_lo_que_puedo import *
from planificacion.strategy.lineal import *
from planificacion.strategy.lineal_continuo import *
from planificacion.dependencias import GerenciadorDependencias
import datetime

ESTRATEGIAS=(
  (0,_(u'Hago lo que puedo')),
  (1,_(u'Programación lineal mixta')),
  (2,_(u'Programación lineal continua (sin dependencias)')),)

CLASES_ESTRATEGIAS={
  0: PlanificadorHagoLoQuePuedo,
  1: PlanificadorModeloLineal,
  2: PlanificadorLinealContinuo, }

class Hueco:
  
  fecha_desde=None
  tiempo=None

  def __init__(self, fecha_desde, tiempo):
    self.fecha_desde = fecha_desde
    self.tiempo = tiempo

class Cronograma(models.Model):
  """
  Validar:
  - intervalo_tiempo no puede ser modificado en caso que existan instancias
  de IntervaloCronograma.
  """
  descripcion = models.CharField(max_length=100, verbose_name=_(u'Descripción'), unique=True)
  intervalo_tiempo = models.DecimalField(
    max_digits=7, decimal_places=2, verbose_name=_(u'Intervalo de Tiempo (min)'), 
    help_text=_(u'Tiempo por cada intervalo que compone el cronograma.'))
  fecha_inicio = models.DateTimeField(
    verbose_name=_(u'Fecha de inicio'), null=True, blank=True, default=datetime.datetime.now())
  estrategia = models.IntegerField(verbose_name=_(u'Estrategia de planificación'), choices=ESTRATEGIAS)

  class Meta:
    ordering = ['-id']
    verbose_name = _(u"Cronograma")
    verbose_name_plural = _(u"Cronogramas")

  def planificar(self):
    """
    Este es el core del producto. Acá es donde en función de la configuración 
    de producción y del cronograma se van a generar los intervalos del 
    cronograma con la planificación correspondiente para llevar a cabo la
    producción.
    """
    IntervaloCronograma.objects.filter(cronograma=self).delete()
    planificador = CLASES_ESTRATEGIAS[self.estrategia](self)
    planificador.planificar()

  def __unicode__(self):
    return self.descripcion

  def get_pedidos(self):
    return [ p.pedido for p in self.pedidocronograma_set.all() ]

  def get_maquinas(self):
    return [ x.maquina for x in self.maquinacronograma_set.all() ]

  def get_maquinas_tarea_producto(self, tarea, producto):
    return [ t.maquina for t in TiempoRealizacionTarea.objects.filter(
      maquina__in=self.get_maquinas(), tarea=tarea,producto=producto) ]

  def add_intervalo(self,secuencia,maquina,tarea,pedido,producto,cantidad_tarea,tiempo_intervalo=None):
    if tiempo_intervalo == None:
      tiempo_intervalo = self.intervalo_tiempo
    intervalo=IntervaloCronograma(cronograma=self,maquina=maquina,secuencia=secuencia,
      tarea=tarea,producto=producto,pedido=pedido,cantidad_tarea=cantidad_tarea,
      tiempo_intervalo=tiempo_intervalo)
    intervalo.clean()
    intervalo.save()

  def get_huecos(self, maquina):
    huecos=[]
    intervalos = self.intervalocronograma_set.filter(maquina=maquina).order_by('fecha_desde')
    intervalo_anterior = None
    for intervalo in intervalos:
      if intervalo.fecha_desde == self.fecha_inicio:
        intervalo_anterior = intervalo
        continue
      if intervalo_anterior is None:
        hueco = Hueco(fecha_desde=self.fecha_inicio,
          tiempo=intervalo.fecha_desde-self.fecha_inicio)
        huecos.append(hueco)
        intervalo_anterior = intervalo
        continue
      if intervalo_anterior.get_fecha_hasta() <> intervalo.get_fecha_desde():
        hueco = Hueco(fecha_desde=intervalo_anterior.get_fecha_hasta(),
          tiempo=intervalo.fecha_desde-intervalo_anterior.get_fecha_hasta())
        huecos.append(hueco)
        intervalo_anterior = intervalo
    return huecos

  def get_ultima_fecha(self, maquina):
    from django.db.models import Max
    ultima_fecha = self.intervalocronograma_set.filter(
      maquina=maquina).aggregate(Max('fecha_desde'))['fecha_desde__max']
    if not ultima_fecha:
      return self.fecha_inicio
    return self.intervalocronograma_set.filter(
      maquina=maquina).get(fecha_desde=ultima_fecha).get_fecha_hasta()

  def add_intervalo_al_final(self, maquina, tarea, producto, pedido, cantidad_tarea):
    intervalo = None
    try:
      intervalo = self.intervalocronograma_set.filter(maquina=maquina).last()
    except IntervaloCronograma.DoesNotExist:
      pass
    if intervalo:
      secuencia = intervalo.secuencia + 1
    else:
      secuencia = 1
    intervalo=IntervaloCronograma(cronograma=self,maquina=maquina,secuencia=secuencia,
      tarea=tarea,producto=producto,pedido=pedido,cantidad_tarea=cantidad_tarea)
    intervalo.clean()
    intervalo.save()

  def add_maquina(self, maquina):
    return self.maquinacronograma_set.create(maquina=maquina)

  def add_pedido(self, pedido):
    return self.pedidocronograma_set.create(pedido=pedido)

  def get_intervalo(self, instante, maquina, tarea, pedido, producto):
    try:
      return self.intervalocronograma_set.get(
        secuencia=instante, maquina=maquina, tarea=tarea, pedido=pedido, producto=producto)
    except IntervaloCronograma.DoesNotExist:
      return None

class PedidoCronograma(models.Model):
  cronograma = models.ForeignKey(Cronograma, verbose_name=_(u'Cronograma'))
  pedido = models.ForeignKey(Pedido, verbose_name=_(u'Pedido'), on_delete=models.PROTECT)

  class Meta:
    ordering = ['pedido__descripcion']
    verbose_name = _(u"Pedido cronograma")
    verbose_name_plural = _(u"Pedidos cronograma")
    unique_together = (('cronograma', 'pedido'),)

  def __unicode__(self):
    return self.pedido

class MaquinaCronograma(models.Model):
  cronograma = models.ForeignKey(Cronograma, verbose_name=_(u'Cronograma'))
  maquina = models.ForeignKey(Maquina, verbose_name=_(u'Máquina'), on_delete=models.PROTECT)

  class Meta:
    ordering = ['maquina__descripcion']
    verbose_name = _(u"Maquina cronograma")
    verbose_name_plural = _(u"Maquina cronograma")
    unique_together = (('cronograma', 'maquina'),)

  def __unicode__(self):
    return self.maquina

class SolapamientoIntervalo(ValidationError):
  pass

class IntervaloCronograma(models.Model):

  cronograma = models.ForeignKey(Cronograma, verbose_name=_(u'Cronograma'))
  maquina = models.ForeignKey(Maquina, verbose_name=_(u'Máquina'), on_delete=models.PROTECT)
  secuencia = models.IntegerField(verbose_name=_(u'Secuencia'),
    help_text=_(u'Secuencia de aparición en el cronograma'), null=True, blank=True)
  tarea = models.ForeignKey(Tarea, verbose_name=_(u'Tarea'), on_delete=models.PROTECT)
  producto = models.ForeignKey(Producto, verbose_name=_(u'Producto'), on_delete=models.PROTECT)
  pedido = models.ForeignKey(Pedido, verbose_name=_(u'Pedido'), on_delete=models.PROTECT)
  cantidad_tarea = models.DecimalField( editable=False, default=0,
    max_digits=7, decimal_places=2, verbose_name=_(u'Cantidad Tarea'),
    help_text=_(u'Cantidad de tarea producida luego de finalizar el intervalo.'))
  cantidad_producto = models.DecimalField( editable=False, default=0,
    max_digits=7, decimal_places=2, verbose_name=_(u'Cantidad Producto'), 
    help_text=_(u'Cantidad de producto producido luego de finalizar el intervalo.'))
  tiempo_intervalo = models.IntegerField(
    verbose_name=_(u'Tiempo del intervalo (min)'))
  fecha_desde = models.DateTimeField(
    verbose_name=_(u'Fecha desde'), null=False, blank=False)

  # atributos exclusivos para asegurar la consistencia de la información
  tareamaquina = models.ForeignKey(TareaMaquina, editable=False, on_delete=models.PROTECT)
  tareaproducto = models.ForeignKey(TareaProducto, editable=False, on_delete=models.PROTECT)
  itempedido = models.ForeignKey(ItemPedido, editable=False, on_delete=models.PROTECT)
  pedidocronograma = models.ForeignKey(PedidoCronograma, editable=False)
  maquinacronograma = models.ForeignKey(MaquinaCronograma, editable=False)

  class Meta:
    ordering = ['-cronograma__id','maquina__descripcion','secuencia']
    verbose_name = _(u"Intervalo cronograma")
    verbose_name_plural = _(u"Intervalos cronograma")
    unique_together = (('cronograma', 'maquina', 'secuencia'),)

  def __unicode__(self):
    return '%s - %s - %s' % (self.maquina.descripcion, self.get_fecha_desde(),
      self.get_fecha_hasta())

  def get_tiempo_tarea(self):
    return self.tarea.get_tiempo(self.maquina,self.producto)

  def get_intervalos_maquina(self):
    return self.cronograma.intervalocronograma_set.filter(maquina=self.maquina)

  def get_intervalos_anteriores_maquina(self):
    """
    Obtiene los intervalos anteriores en misma máquina y mismo crono
    """
    return self.get_intervalos_maquina().filter(secuencia__lt=self.secuencia)

  def calcular_fecha_desde(self):
    if self.fecha_desde:
      return
    intervalos = self.get_intervalos_anteriores_maquina()
    if len(intervalos) == 0:
      tiempo_anterior = 0
    else:
      tiempo_anterior = intervalos.aggregate(models.Sum('tiempo_intervalo'))['tiempo_intervalo__sum']
    self.fecha_desde = self.cronograma.fecha_inicio + datetime.timedelta(minutes=tiempo_anterior)

  def get_fecha_desde(self):
    return self.fecha_desde

  def get_fecha_hasta(self):
    return self.get_fecha_desde() + datetime.timedelta(minutes=self.tiempo_intervalo)

  def calcular_cantidad_tarea(self):
    if self.cantidad_tarea:
      return
    self.cantidad_tarea = self.tiempo_intervalo / float(self.tarea.get_tiempo(self.maquina,self.producto))

  def validar_solapamiento(self):
    intervalos_maquina = IntervaloCronograma.objects.filter(
      cronograma=self.cronograma,maquina=self.maquina)
    for intervalo in intervalos_maquina:
      if ( intervalo.get_fecha_desde() <= self.get_fecha_desde() and
        intervalo.get_fecha_hasta() > self.get_fecha_desde() ) or\
        ( intervalo.get_fecha_desde() < self.get_fecha_hasta() and
        intervalo.get_fecha_hasta() >= self.get_fecha_hasta() ) or\
        ( self.get_fecha_desde() <= intervalo.get_fecha_desde() and
        self.get_fecha_hasta() >= intervalo.get_fecha_hasta() ):
        raise SolapamientoIntervalo(
          _(u'Ha ocurrido solapamiento entre el intervalo %s y el intervalo %s:') %
          (self, intervalo))

  def validar_dependencias_guardado(self):
    self.validar_solapamiento()
    gerenciador_dependencias = GerenciadorDependencias.crear_desde_instante(self)
    if self.id:
      gerenciador_dependencias.verificar_modificar_instante(self)
    else:
      gerenciador_dependencias.verificar_agregar_instante(self)

  def validar_dependencias_borrado(self):
    gerenciador_dependencias = GerenciadorDependencias.crear_desde_instante(self)
    gerenciador_dependencias.verificar_eliminar_instante(self)

  def clean(self):
    self.tareamaquina = TareaMaquina.objects.get(tarea=self.tarea,maquina=self.maquina)
    self.tareaproducto = TareaProducto.objects.get(tarea=self.tarea,producto=self.producto)
    self.itempedido = ItemPedido.objects.get(pedido=self.pedido,producto=self.producto)
    self.pedidocronograma = PedidoCronograma.objects.get(pedido=self.pedido,cronograma=self.cronograma)
    self.maquinacronograma = MaquinaCronograma.objects.get(maquina=self.maquina,cronograma=self.cronograma)
    self.calcular_fecha_desde()
    self.calcular_cantidad_tarea()

  def delete(self, *args, **kwargs):
    self.validar_dependencias_borrado()
    super(IntervaloCronograma, self).delete(*args, **kwargs) 

  def save(self, *args, **kwargs):
    self.validar_dependencias_guardado()
    super(IntervaloCronograma, self).save(*args, **kwargs) 

def validar_dependencias_borrado(sender, instance, **kwargs):
  gerenciador_dependencias = GerenciadorDependencias.crear_desde_instante(instance)
  gerenciador_dependencias.verificar_eliminar_instante(instance)

from django.db.models.signals import pre_delete

#pre_delete.connect(validar_dependencias_borrado, 
  #sender=IntervaloCronograma)
