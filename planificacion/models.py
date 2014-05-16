# coding=utf-8
from django.db import models
from produccion.models import *
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from planificacion.strategy.hago_lo_que_puedo import *
from planificacion.strategy.lineal import *
from planificacion.strategy import lineal_continuo 
from planificacion.dependencias import GerenciadorDependencias
from django.core.exceptions import ValidationError
import datetime
from decimal import Decimal

ESTRATEGIAS=(
  (2,_(u'PLM (Modelo Tiempo Contínuo) + Heurística basada en dependencias')),)

CLASES_ESTRATEGIAS={
  0: PlanificadorHagoLoQuePuedo,
  1: PlanificadorModeloLineal,
  2: lineal_continuo.PlanificadorLinealContinuo, }

class Hueco(object):
  
  fecha_desde=None
  tiempo=None

  def __init__(self, fecha_desde, tiempo=None, fecha_hasta=None):
    if tiempo and fecha_hasta or not (tiempo or fecha_hasta):
      raise Exception(_('Debe informa el tiempo del hueco o la fecha hasta'))
    self.fecha_desde = fecha_desde
    if tiempo:
      self.tiempo = tiempo
    else:
      self.tiempo = fecha_hasta - fecha_desde

  def __unicode__(self):
    return u'(%s,%s)' % (self.fecha_desde, self.get_fecha_hasta())

  def get_fecha_hasta(self):
    return self.fecha_desde + self.tiempo

class PedidoYaDistribuido(ValidationError):
  pass

class Cronograma(models.Model):
  """
  Validar:
  - intervalo_tiempo no puede ser modificado en caso que existan instancias
  de IntervaloCronograma.
  """
  descripcion = models.CharField(max_length=100, verbose_name=_(u'Descripción'), unique=True)
  fecha_inicio = models.DateTimeField(
    verbose_name=_(u'Fecha de inicio'), null=True, blank=True, default=datetime.datetime.now())
  estrategia = models.IntegerField(verbose_name=_(u'Estrategia de planificación'), choices=ESTRATEGIAS, default=2)
  tiempo_minimo_intervalo = models.DecimalField(default=0,
    max_digits=7, decimal_places=2, verbose_name=_(u'Tiempo mínimo de cada intervalo (min)'), 
    help_text=_(u'Tiempo mínimo de cada intervalo que compone el cronograma. NO será tenido en cuenta durante la resolución del modelo lineal. Esto quiere decir que si la resolución del modelo lineal obtiene intervalos con tiempo menor al definido, estos serán incorporados al cronograma.'))
  optimizar_planificacion = models.BooleanField(default=True, verbose_name=(u'Optimizar planificación'),
    help_text=_(u'Una vez obtenida la planificación intenta optimizarla un poco más.'))

  class Meta:
    ordering = ['-id']
    verbose_name = _(u"Cronograma")
    verbose_name_plural = _(u"Cronogramas")

  def get_ids_posibles_maquinas_cuello_botella(self):
    maquinas_y_tiempos = self.intervalocronograma_set.values(
      'maquina').annotate(tiempo_intervalo=models.Sum(
        'tiempo_intervalo')).order_by( '-tiempo_intervalo')
    tiempo_cuello_botella = None
    resultado=[]
    for x in maquinas_y_tiempos:
      if len(resultado) == 0:
        tiempo_cuello_botella = x['tiempo_intervalo']
      if x['tiempo_intervalo']<tiempo_cuello_botella:
        break
      resultado.append(x['maquina'])
    return resultado

  def get_ids_maquinas_cuello_botella(self):
    result = set()
    posibles = self.get_ids_posibles_maquinas_cuello_botella()
    tareas_maquinas_restantes = set()
    for x in MaquinaCronograma.objects.exclude(
      maquina__id__in=posibles):
      tareas_maquinas_restantes = tareas_maquinas_restantes | set(x.maquina.get_tareas())
    for maquina in Maquina.objects.filter(id__in=posibles):
      if maquina.tareamaquina_set.filter(
        tarea__in=tareas_maquinas_restantes).count() == 0:
        result.add(maquina.id) 
    return result

  def is_maquina_cuello_botella(self, maquina):
    return maquina.id in self.get_ids_maquinas_cuello_botella()

  def test_distribuir(self):
    pedidos_ya_distribuidos =\
      [ p.pedido.descripcion for p in CronogramaActivo.get_instance().pedidocronograma_set.filter(
        pedido__in=self.get_pedidos()) ]
    if len(pedidos_ya_distribuidos)>0:
      raise PedidoYaDistribuido(_(u'Los siguientes pedidos ya han sido distribuidos: %s ') %
        pedidos_ya_distribuidos)

  def has_maquina(self, maquina):
    try:
      self.maquinacronograma_set.get(cronograma=self,maquina=maquina)
      return True
    except MaquinaCronograma.DoesNotExist:
      pass
    return False

  def distribuir(self):

    self.test_distribuir()

    cronograma_activo = CronogramaActivo.get_instance()

    for pedido in self.get_pedidos():
      cronograma_activo.add_pedido(pedido)

    for maquina in self.get_maquinas():
      if not cronograma_activo.has_maquina(maquina):
        cronograma_activo.add_maquina(maquina)

    intervalos = [ i for i in self.intervalocronograma_set.all().order_by('fecha_desde') ]
    ids_intervalos_copiados = []
    while len(intervalos) > len(ids_intervalos_copiados):
      for intervalo in intervalos:
        if intervalo.id in ids_intervalos_copiados:
          continue
        id_intervalo = intervalo.id
        intervalo.id = None
        intervalo.cronograma = cronograma_activo
        try:
          intervalo.clean()
          intervalo.save()
          ids_intervalos_copiados.append(id_intervalo)
        except ValidationError:
          pass

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

  def get_intervalos(self):
    return self.intervalocronograma_set.all()

  def get_intervalos_maquina(self, maquina):
    return self.intervalocronograma_set.filter(maquina=maquina)

  def get_pedidos(self):
    return [ p.pedido for p in self.pedidocronograma_set.all() ]

  def get_maquinas(self):
    return [ x.maquina for x in self.maquinacronograma_set.all() ]

  def get_maquinas_tarea_producto(self, tarea, producto):
    return [ t.maquina for t in TiempoRealizacionTarea.objects.filter(
      maquina__in=self.get_maquinas(), tarea=tarea,producto=producto, activa=True) ]

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
      if not intervalo_anterior:
        intervalo_anterior = intervalo
        if intervalo.fecha_desde > intervalo.cronograma.fecha_inicio:
          fecha_desde = intervalo.cronograma.fecha_inicio
          fecha_hasta = intervalo.fecha_desde
        else:
          continue
      else:
        if intervalo.fecha_desde > intervalo_anterior.get_fecha_hasta():
          fecha_desde = intervalo_anterior.get_fecha_hasta()
          fecha_hasta = intervalo.fecha_desde
          intervalo_anterior = intervalo
        else:
          intervalo_anterior = intervalo
          continue
      hueco = Hueco(fecha_desde=fecha_desde,
        tiempo=fecha_hasta-fecha_desde)
      huecos.append(hueco)
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

class IntervaloAnteriorNoExiste(Exception):
  pass

class HuecoAdyacenteAnteriorNoExiste(Exception):
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
  tiempo_intervalo = models.DecimalField(
    max_digits=7, decimal_places=2,
    verbose_name=_(u'Tiempo del intervalo (min)'))
  fecha_desde = models.DateTimeField(
    verbose_name=_(u'Fecha desde'), null=False, blank=False)
  fecha_hasta = models.DateTimeField(
    verbose_name=_(u'Fecha hasta'), null=True, blank=False)

  # atributos exclusivos para asegurar la consistencia de la información
  tareamaquina = models.ForeignKey(TareaMaquina, editable=False, on_delete=models.PROTECT)
  tareaproducto = models.ForeignKey(TareaProducto, editable=False, on_delete=models.PROTECT)
  itempedido = models.ForeignKey(ItemPedido, editable=False, on_delete=models.PROTECT)
  pedidocronograma = models.ForeignKey(PedidoCronograma, editable=False)
  maquinacronograma = models.ForeignKey(MaquinaCronograma, editable=False)

  class Meta:
    ordering = ['-cronograma__id', 'fecha_desde']
    verbose_name = _(u"Intervalo cronograma")
    verbose_name_plural = _(u"Intervalos cronograma")
    unique_together = (('cronograma', 'maquina', 'secuencia'),)

  def __unicode__(self):
    return '#%s(%s, %s, ped #%s, %s, cant: %s, %s, %s)' % (self.id,
      self.maquina.descripcion, self.tarea.descripcion, self.pedido.id,
      self.producto.descripcion, self.cantidad_tarea,
      self.get_fecha_desde(), self.get_fecha_hasta())

  def in_maquina_cuello_botella(self):
    return self.cronograma.is_maquina_cuello_botella(self.maquina)
  in_maquina_cuello_botella.short_description = _(u'Cuello Botella')

  def get_intervalo_anterior(self):

    try:
      fecha_desde_anterior = IntervaloCronograma.objects.filter(maquina=self.maquina, 
        fecha_desde__lt=self.fecha_desde).aggregate(models.Max('fecha_desde'))['fecha_desde__max']
      return self.cronograma.intervalocronograma_set.get(maquina=self.maquina, 
        fecha_desde=fecha_desde_anterior)
    except IntervaloCronograma.DoesNotExist:
      pass

    raise IntervaloAnteriorNoExiste()

  def get_hueco_adyacente_anterior(self):

    if self.fecha_desde == self.cronograma.fecha_inicio:
      raise HuecoAdyacenteAnteriorNoExiste()

    try:
      intervalo_anterior = self.get_intervalo_anterior()
    except IntervaloAnteriorNoExiste:
      return Hueco(self.cronograma.fecha_inicio, fecha_hasta=self.fecha_desde)

    if intervalo_anterior.get_fecha_hasta() == self.get_fecha_desde():
      raise HuecoAdyacenteAnteriorNoExiste()
      
    return Hueco(intervalo_anterior.get_fecha_hasta(), fecha_hasta=self.fecha_desde)
      

  def mover(self, minutos):
    self.fecha_desde += datetime.timedelta(minutes=minutos)

  def get_tiempo_tarea(self):
    return self.tarea.get_tiempo(self.maquina,self.producto)

  def get_intervalos_maquina(self):
    return self.cronograma.get_intervalos_maquina(self.maquina)

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
    self.fecha_desde = self.cronograma.fecha_inicio + datetime.timedelta(seconds=int(tiempo_anterior*60))

  def calcular_fecha_hasta(self):
    self.fecha_hasta = self.get_fecha_hasta()

  def get_fecha_desde(self):
    return self.fecha_desde

  def get_fecha_hasta(self):
    return self.get_fecha_desde() + datetime.timedelta(seconds=int(self.tiempo_intervalo*60))

  def calcular_cantidad_tarea(self):
    if self.cantidad_tarea:
      return
    self.cantidad_tarea = Decimal(self.tiempo_intervalo) / Decimal(self.tarea.get_tiempo(self.maquina,self.producto))

  def validar_solapamiento(self):
    if self.id:
      intervalos_maquina = IntervaloCronograma.objects.exclude(pk=self.id)
    else:
      intervalos_maquina = IntervaloCronograma.objects
    intervalos_maquina = intervalos_maquina.filter(
      cronograma=self.cronograma,maquina=self.maquina)
    for intervalo in intervalos_maquina:
      if ( intervalo.get_fecha_desde() <= self.get_fecha_desde() and
        intervalo.get_fecha_hasta() > self.get_fecha_desde() ) or\
        ( intervalo.get_fecha_desde() < self.get_fecha_hasta() and
        intervalo.get_fecha_hasta() >= self.get_fecha_hasta() ) or\
        ( self.get_fecha_desde() <= intervalo.get_fecha_desde() and
        self.get_fecha_hasta() >= intervalo.get_fecha_hasta() ):
        raise SolapamientoIntervalo(
          _(u'Ha ocurrido solapamiento entre el intervalo que está siendo validado %s y el intervalo %s:') %
          (self, intervalo))

  def validar_dependencias_guardado(self):
    gerenciador_dependencias = GerenciadorDependencias.crear_desde_instante(self)
    if self.id:
      gerenciador_dependencias.verificar_modificar_instante(self)
    else:
      gerenciador_dependencias.verificar_agregar_instante(self)

  def validar_dependencias_borrado(self):
    gerenciador_dependencias = GerenciadorDependencias.crear_desde_instante(self)
    gerenciador_dependencias.verificar_eliminar_instante(self)

  def validar_fecha_inicio_cronograma(self):
    if self.fecha_desde < self.cronograma.fecha_inicio:
      raise ValidationError(_('Fecha desde %s anterior a la fecha de inicio del cronograma %s') % (
        self.fecha_desde, self.cronograma.fecha_inicio))

  def clean(self):
    self.tareamaquina = TareaMaquina.objects.get(tarea=self.tarea,maquina=self.maquina)
    self.tareaproducto = TareaProducto.objects.get(tarea=self.tarea,producto=self.producto)
    self.itempedido = ItemPedido.objects.get(pedido=self.pedido,producto=self.producto)
    self.pedidocronograma = PedidoCronograma.objects.get(pedido=self.pedido,cronograma=self.cronograma)
    self.maquinacronograma = MaquinaCronograma.objects.get(maquina=self.maquina,cronograma=self.cronograma)
    self.calcular_fecha_desde()
    self.calcular_cantidad_tarea()
    self.calcular_fecha_hasta()
    self.validar_solapamiento()
    self.validar_dependencias_guardado()
    self.validar_fecha_inicio_cronograma()

  def delete(self, *args, **kwargs):
    self.validar_dependencias_borrado()
    super(IntervaloCronograma, self).delete(*args, **kwargs) 

  def save(self, *args, **kwargs):
    super(IntervaloCronograma, self).save(*args, **kwargs) 

def validar_dependencias_borrado(sender, instance, **kwargs):
  gerenciador_dependencias = GerenciadorDependencias.crear_desde_instante(instance)
  gerenciador_dependencias.verificar_eliminar_instante(instance)

from django.db.models.signals import pre_delete

#pre_delete.connect(validar_dependencias_borrado, 
  #sender=IntervaloCronograma)

"""
class CronogramaActivo(Cronograma):

  instance = None

  def planificar(self):
    raise CronogramaActivoNoPlanificable()

  @staticmethod
  def get_instance():
    try:
      instance = CronogramaActivo.objects.first()
    except CronogramaActivo.DoesNotExists:
      pass
    if not instance:
      instance = CronogramaActivo(fecha_inicio=datetime.datetime(1,1,1))
      instance.clean()
      instance.save()
    return instance

def add_maquina_to_cronograma_activo(sender, instance, created, **kwargs):
  if not created:
    return
  CronogramaActivo.get_instance().add_maquina(instance)

post_save.connect(add_maquina_to_cronograma_activo, 
  sender=Maquina)
"""

def add_maquinas_posibles_to_cronograma(sender, instance, created, **kwargs):
  if not created:
    return
  if not instance.pedido:
    return
  if not instance.cronograma:
    return
  for maquina in instance.pedido.get_maquinas_posibles_produccion():
    if not instance.cronograma.has_maquina(maquina):
      instance.cronograma.add_maquina(maquina)

post_save.connect(add_maquinas_posibles_to_cronograma, 
  sender=PedidoCronograma)
