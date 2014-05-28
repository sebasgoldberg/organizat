# coding=utf-8
from django.db import models
from produccion.models import *
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from planificacion.strategy.hago_lo_que_puedo import PlanificadorHagoLoQuePuedo
from planificacion.strategy import lineal_continuo 
from planificacion.dependencias import GerenciadorDependencias
from django.core.exceptions import ValidationError
import datetime
from decimal import Decimal
from django.db import transaction
from django.utils import timezone as TZ
from datetime import timedelta as TD

"""
Excepcione de validación de tareas reales.
"""

class TareaRealEnCronogramaInactivo(ValidationError):
  pass

class TareaRealSuperaPlanificada(ValidationError):
  pass

class TareaRealNoRespetaDependencias(ValidationError):
  pass

"""
Excepciones de validación de cambios de estado en intervalos.
"""

class IntervaloFinalizadoEnCronogramaInactivo(ValidationError):
  pass

class IntervaloCanceladoEnCronogramaInactivo(ValidationError):
  pass

class IntervaloEnCursoEnCronogramaInactivo(ValidationError):
  pass

class IntervaloFinalizadoConCantidadNula(ValidationError):
  pass

class IntervaloCanceladoConCantidadNoNula(ValidationError):
  pass

class IntervaloDistintoPlanificadoEnCronogramaInactivo(ValidationError):
  pass

ESTRATEGIAS=(
  (2,_(u'PLM (Modelo Tiempo Contínuo) + Heurística basada en dependencias')),)

CLASES_ESTRATEGIAS={
  0: PlanificadorHagoLoQuePuedo,
  2: lineal_continuo.PlanificadorLinealContinuo, }

ESTADO_CRONOGRAMA_NO_PLANIFICADO=0
ESTADO_CRONOGRAMA_VALIDO=1
ESTADO_CRONOGRAMA_ACTIVO=2
ESTADO_CRONOGRAMA_INVALIDO=3

ESTADOS_CRONOGRAMAS=(
  (ESTADO_CRONOGRAMA_NO_PLANIFICADO,_(u'No planificado')),
  (ESTADO_CRONOGRAMA_VALIDO,_(u'Válido')),
  (ESTADO_CRONOGRAMA_ACTIVO,_(u'Activo')),
  (ESTADO_CRONOGRAMA_INVALIDO,_(u'Inválido')),
  )

ESTADO_INTERVALO_PLANIFICADO=0
ESTADO_INTERVALO_EN_CURSO=1
ESTADO_INTERVALO_FINALIZADO=2
ESTADO_INTERVALO_CANCELADO=3

ESTADOS_INTERVALOS=(
  (ESTADO_INTERVALO_PLANIFICADO,_(u'Planificado')),
  (ESTADO_INTERVALO_EN_CURSO,_(u'En curso')),
  (ESTADO_INTERVALO_FINALIZADO,_(u'Finalizado')),
  (ESTADO_INTERVALO_CANCELADO,_(u'Cancelado')),
)

class Hueco(object):
  
  fecha_desde=None
  tiempo=None

  def __init__(self, fecha_desde, tiempo=None, fecha_hasta=None):
    if tiempo and fecha_hasta or not (tiempo or fecha_hasta):
      raise Exception(_('Debe informa el tiempo del hueco o la fecha hasta'))
    if fecha_desde.tzinfo is None:
      self.fecha_desde = TZ.make_aware(
        fecha_desde, TZ.get_default_timezone())
    else:
      self.fecha_desde = fecha_desde
    if tiempo:
      self.tiempo = tiempo
    else:
      self.tiempo = fecha_hasta - fecha_desde

  def __unicode__(self):
    return u'(%s,%s)' % (self.fecha_desde, self.get_fecha_hasta())

  def get_fecha_hasta(self):
    return self.fecha_desde + self.tiempo

  def solapado(self, hueco):
    fecha_desde = max(self.fecha_desde, hueco.fecha_desde)
    fecha_hasta = min(self.get_fecha_hasta(), hueco.get_fecha_hasta())

    return fecha_desde <= fecha_hasta

  def unir(self, hueco):

    if not self.solapado(hueco):
      raise HuecoNoSolapado()

    fecha_desde = min(self.fecha_desde, hueco.fecha_desde)
    fecha_hasta = max(self.get_fecha_hasta(), hueco.get_fecha_hasta())

    return Hueco(fecha_desde, fecha_hasta=fecha_hasta)

  def get_minutos(self):
    return float(self.tiempo.total_seconds()) / 60

  @staticmethod
  def union(lh1, lh2):
    """
    Realiza la union de los 2 listados de huecos.
    En caso que exista solapamiento entre huecos, realiza su unión.
    precondiciones:
    - lh1 y lh2 están ordenados por fecha_desde.
    - Cada hueco de lh1 no presentan solapamientos entre si.
    - Cada hueco de lh2 no presentan solapamientos entre si.
    """
    i1 = 0
    i2 = 0
    len1 = len(lh1)
    len2 = len(lh2)
    solapados = []
    h1 = None
    h2 = None
    h_unido = None
    resultado = []
    while i1 < len1 or i2 < len2:

      if i1 < len1:
        h1 = lh1[i1]
      else:
        h1 = None

      if i2 < len2:
        h2 = lh2[i2]
      else:
        h2 = None

      if h1 is None:
        h = h2
        i2 += 1
      elif h2 is None:
        h = h1
        i1 += 1
      elif h1.fecha_desde < h2.fecha_desde:
        h = h1
        i1 += 1
      else:
        h = h2
        i2 += 1

      if h_unido is None:
        h_unido = h
        continue

      if h_unido.solapado(h):
        h_unido = h_unido.unir(h)
      else:
        resultado.append(h_unido)
        h_unido = h

    if h_unido is not None:
      resultado.append(h_unido)

    return resultado



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
  estado = models.IntegerField(verbose_name=_(u'Estado'), choices=ESTADOS_CRONOGRAMAS, default=0)

  class Meta:
    ordering = ['-id']
    verbose_name = _(u"Cronograma")
    verbose_name_plural = _(u"Cronogramas")

  def get_cantidad_real_tarea(self, tarea, ids_intervalos_excluir=[]):
    qs = self.intervalocronograma_set.filter(tarea=tarea).exclude(
      id__in=ids_intervalos_excluir).aggregate(total_real=models.Sum(
        'cantidad_tarea_real'))
    if qs['total_real'] is None:
      return 0
    return qs['total_real']

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

  @transaction.atomic
  def planificar(self):
    """
    Este es el core del producto. Acá es donde en función de la configuración 
    de producción y del cronograma se van a generar los intervalos del 
    cronograma con la planificación correspondiente para llevar a cabo la
    producción.
    """
    self.estado = ESTADO_CRONOGRAMA_NO_PLANIFICADO
    self.clean()
    IntervaloCronograma.objects.filter(cronograma=self).delete()
    planificador = CLASES_ESTRATEGIAS[self.estrategia](self)
    planificador.planificar()
    self.estado = ESTADO_CRONOGRAMA_VALIDO
    self.clean()
    self.save()

  def is_valido(self):
    return self.estado == ESTADO_CRONOGRAMA_VALIDO

  def is_activo(self):
    return self.estado == ESTADO_CRONOGRAMA_ACTIVO

  def desactivar(self):
    if self.is_activo():
      self.estado = ESTADO_CRONOGRAMA_VALIDO
    self.clean()
    self.save()

  @transaction.atomic
  def activar(self):
    if self.is_activo():
      raise ValidationError(_(u'El cronograma ya se encuentra activo'))
    if not self.is_valido():
      self.planificar()
    self.estado = ESTADO_CRONOGRAMA_ACTIVO
    self.save()
    Cronograma.invalidar_cronogramas_validos()

  @staticmethod
  def invalidar_cronogramas_validos():
    for cronograma in Cronograma.objects.filter(estado=ESTADO_CRONOGRAMA_VALIDO):
      cronograma.estado = ESTADO_CRONOGRAMA_INVALIDO
      cronograma.clean()
      cronograma.save()

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

  def get_intervalos_propios_y_activos(self, maquina):
    intervalos_propios = IntervaloCronograma.objects.filter(
      cronograma=self,
      maquina=maquina)
    intervalos_activos = IntervaloCronograma.objects.filter(
      maquina=maquina,
      cronograma__estado=ESTADO_CRONOGRAMA_ACTIVO, 
      fecha_hasta__gte=self.fecha_inicio)
    return intervalos_propios | intervalos_activos

  def get_huecos(self, maquina):
    intervalos = self.get_intervalos_propios_y_activos(maquina).order_by('fecha_desde')
    intervalo_anterior = None
    fecha_desde = None
    fecha_hasta = None
    calendario = maquina.get_calendario()
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
      for hueco in calendario.get_huecos(fecha_desde, fecha_hasta):
        yield hueco
    
    # Ojo! No termina nunca!
    desde = None
    if fecha_hasta is None:
      desde = self.fecha_inicio
    else:
      desde = fecha_hasta

    un_anyo = TD(days=365) 
    while True:
      for hueco in calendario.get_huecos(desde,tiempo_total=un_anyo):
        yield hueco
      desde = desde + un_anyo

  def get_ultima_fecha(self, maquina):
    from django.db.models import Max
    ultima_fecha = self.get_intervalos_propios_y_activos(
      maquina).aggregate(Max('fecha_desde'))['fecha_desde__max']
    if not ultima_fecha:
      return self.fecha_inicio
    return self.get_intervalos_propios_y_activos(
      maquina).get(fecha_desde=ultima_fecha).get_fecha_hasta()

  def add_intervalo_al_final(self, maquina, tarea, producto, pedido, cantidad_tarea):
    intervalo=IntervaloCronograma(cronograma=self,maquina=maquina,
      tarea=tarea,producto=producto,pedido=pedido,cantidad_tarea=cantidad_tarea)
    intervalo.clean()
    intervalo.save()

  def add_maquina(self, maquina):
    return self.maquinacronograma_set.create(maquina=maquina)

  def add_pedido(self, pedido):
    return self.pedidocronograma_set.create(pedido=pedido)

  def validar_estado(self):
    if not self.is_activo():

      cantidad_con_tarea_real= self.intervalocronograma_set.filter(
        cantidad_tarea_real__gt=0).count()
      if cantidad_con_tarea_real > 0:
        raise TareaRealEnCronogramaInactivo(
          _(u'Imposible desactivar un cronograma con intervalos que presentan '+
          u'cantidades de tarea real mayor a cero.'))

      cantidad_no_planificados = self.intervalocronograma_set.exclude(
        estado=ESTADO_INTERVALO_PLANIFICADO).count()
      if cantidad_no_planificados > 0:
        raise IntervaloDistintoPlanificadoEnCronogramaInactivo(
          _(u'Imposible desactivar un cronograma con intervalos con estado '+
          u'distinto de planificado.'))

  def clean(self):
    self.validar_estado()

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
  tarea = models.ForeignKey(Tarea, verbose_name=_(u'Tarea'), on_delete=models.PROTECT)
  producto = models.ForeignKey(Producto, verbose_name=_(u'Producto'), on_delete=models.PROTECT)
  pedido = models.ForeignKey(Pedido, verbose_name=_(u'Pedido'), on_delete=models.PROTECT)
  cantidad_tarea = models.DecimalField( editable=False, default=0,
    max_digits=7, decimal_places=2, verbose_name=_(u'Cantidad Tarea Planificada'),
    help_text=_(u'Cantidad de tarea a producir en el intervalo.'))
  cantidad_tarea_real = models.DecimalField( editable=False, default=0,
    max_digits=7, decimal_places=2, verbose_name=_(u'Cantidad Tarea Real'), 
    help_text=_(u'Cantidad de tarea producida (real).'))
  tiempo_intervalo = models.DecimalField(
    max_digits=7, decimal_places=2,
    verbose_name=_(u'Tiempo del intervalo (min)'))
  fecha_desde = models.DateTimeField(
    verbose_name=_(u'Fecha desde'), null=False, blank=False)
  fecha_hasta = models.DateTimeField(
    verbose_name=_(u'Fecha hasta'), null=True, blank=False)
  estado = models.IntegerField(verbose_name=_(u'Estado'), choices=ESTADOS_INTERVALOS, default=0)

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
    unique_together = (('cronograma', 'maquina', 'fecha_desde'),)

  def __unicode__(self):
    return '#%s(%s, %s, ped #%s, %s, cant: %s, %s, %s)' % (self.id,
      self.maquina.descripcion, self.tarea.descripcion, self.pedido.id,
      self.producto.descripcion, self.cantidad_tarea,
      self.get_fecha_desde(), self.get_fecha_hasta())

  def iniciar(self):
    self.estado = ESTADO_INTERVALO_EN_CURSO
    self.clean()
    self.save()

  def finalizar(self, cantidad_tarea_real=None):
    if cantidad_tarea_real is not None:
      self.cantidad_tarea_real = cantidad_tarea_real
    self.estado = ESTADO_INTERVALO_FINALIZADO
    self.clean()
    self.save()

  def cancelar(self):
    self.cantidad_tarea_real = 0
    self.estado = ESTADO_INTERVALO_CANCELADO
    self.clean()
    self.save()

  def in_maquina_cuello_botella(self):
    return self.cronograma.is_maquina_cuello_botella(self.maquina)
  in_maquina_cuello_botella.short_description = _(u'Cuello Botella')

  def get_intervalo_anterior(self):

    try:

      fecha_desde_anterior = self.cronograma.get_intervalos_propios_y_activos(
        self.maquina).filter(fecha_desde__gte=self.cronograma.fecha_inicio,
        fecha_desde__lt=self.fecha_desde).aggregate(
        models.Max('fecha_desde'))['fecha_desde__max']

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

  def calcular_fecha_desde(self):
    if self.fecha_desde:
      return
    intervalos = self.get_intervalos_maquina()
    if len(intervalos) == 0:
      self.fecha_desde = self.cronograma.fecha_inicio
    else:
      self.fecha_desde = intervalos.order_by('fecha_desde').last().get_fecha_hasta()

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
    intervalos_maquina = self.cronograma.get_intervalos_propios_y_activos(self.maquina)
    if self.id:
      intervalos_maquina = intervalos_maquina.exclude(pk=self.id)
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

  def validar_cantidad_real_dependencias(self):

    if self.cantidad_tarea_real > 0:
      cantidades_reales_tareas = {}
      for listado_dependencias in self.producto.get_listado_secuencias_dependencias():
        tarea_anterior = None
        for tarea in listado_dependencias:
          if not tarea.id in cantidades_reales_tareas:
            cantidades_reales_tareas[tarea.id] = self.cronograma.get_cantidad_real_tarea(
              tarea, ids_intervalos_excluir=[self.id])
            if tarea.id == self.tarea.id:
              cantidades_reales_tareas[tarea.id] += self.cantidad_tarea_real
          if tarea_anterior is not None:
            if cantidades_reales_tareas[tarea.id] > cantidades_reales_tareas[tarea_anterior.id]:
              raise TareaRealNoRespetaDependencias(_(u'La cantidad real %s de la tarea %s '+
                u'no puede superar la cantidad %s de la tarea %s de la cual '+
                u'depende.') % (cantidades_reales_tareas[tarea.id], tarea,
                cantidades_reales_tareas[tarea_anterior.id], tarea_anterior))
          tarea_anterior = tarea

  def validar_cantidad_real(self):
    if self.cantidad_tarea_real > 0:
      # Se verifica estado del cronograma para poder asignar cantidad real.
      if not self.cronograma.is_activo():
        raise TareaRealEnCronogramaInactivo(_(u'La cantidad de tarea real solo puede ser asignada en intervalos pertenecientes a cronogramas activos.'))

    if self.cantidad_tarea_real > self.cantidad_tarea:
      raise TareaRealSuperaPlanificada(_(u'La cantidad de tarea real %s supera la cantidad de tarea planificada %s.' %(
        self.cantidad_tarea_real, self.cantidad_tarea)))

    # Se valida que dependencias tengan cantidad real mayor o igual.
    self.validar_cantidad_real_dependencias()

  def is_finalizado(self):
    return self.estado == ESTADO_INTERVALO_FINALIZADO

  def is_cancelado(self):
    return self.estado == ESTADO_INTERVALO_CANCELADO

  def is_en_curso(self):
    return self.estado == ESTADO_INTERVALO_EN_CURSO

  def validar_estado(self):
    if not self.cronograma.is_activo():

      if self.is_en_curso():
        raise IntervaloEnCursoEnCronogramaInactivo(
          _(u'Para poder iniciar el intervalo %s, primero debe activar el cronograma %s.') % (
          self, self.cronograma))

      if self.is_finalizado():
        raise IntervaloFinalizadoEnCronogramaInactivo(
          _(u'Para poder finalizar el intervalo %s, primero debe activar el cronograma %s.') % (
          self, self.cronograma))

      if self.is_cancelado():
        raise IntervaloCanceladoEnCronogramaInactivo(
          _(u'Para poder cancelar el intervalo %s, primero debe activar el cronograma %s.') % (
          self, self.cronograma))

    if self.is_finalizado() and self.cantidad_tarea_real == 0:
      raise IntervaloFinalizadoConCantidadNula(
        _(u'Para poder finalizar el intervalo %s debe informar '+
        u'la cantidad de tarea real producida.') % self)

    if self.is_cancelado() and self.cantidad_tarea_real > 0:
      raise IntervaloCanceladoConCantidadNoNula(
        _(u'Para poder cancelar el intervalo %s debe dejar en cero '+
        u'la cantidad de tarea real producida.') % self)

  def clean(self):
    self.tareamaquina = TareaMaquina.objects.get(tarea=self.tarea,maquina=self.maquina)
    self.tareaproducto = TareaProducto.objects.get(tarea=self.tarea,producto=self.producto)
    self.itempedido = ItemPedido.objects.get(pedido=self.pedido,producto=self.producto)
    self.pedidocronograma = PedidoCronograma.objects.get(pedido=self.pedido,cronograma=self.cronograma)
    self.maquinacronograma = MaquinaCronograma.objects.get(maquina=self.maquina,cronograma=self.cronograma)
    self.calcular_fecha_desde()
    self.calcular_cantidad_tarea()
    self.calcular_fecha_hasta()
    self.validar_estado()
    self.validar_cantidad_real()
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
