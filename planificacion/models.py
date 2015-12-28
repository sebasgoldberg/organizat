# coding=utf-8
from django.db import models
from produccion.models import *
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from planificacion.strategy import PlanificadorHagoLoQuePuedo
from planificacion.strategy import PlanificadorLinealContinuo
from planificacion.dependencias import GerenciadorDependencias
from django.core.exceptions import ValidationError
import datetime
from decimal import Decimal
from django.db import transaction
from django.utils import timezone as TZ
from datetime import timedelta as TD
import logging
from utils import Hueco
import calendario.models
from decimal import Decimal as D
from django.db.models import Min, Max
import math
from cleansignal.models import CleanSignal
from django.utils.timezone import now as tz_now
import django.dispatch
cronograma_planificado = django.dispatch.Signal(providing_args=["instance", ])

class PlanificacionBaseModel(CleanSignal):
  class Meta:
    abstract = True
    app_label = 'planificacion'

logger = logging.getLogger(__name__)

class PedidoYaParticionado(ValidationError):
    pass

class ProductoConPlanificacionExistente(ValidationError):
    pass

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
Excepciones de validación de cambios de estado.
"""

class EstadoCronogramaError(ValidationError):
  pass

class EstadoIntervaloCronogramaError(ValidationError):
  pass

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

class IntervaloNoActivoException(ValidationError):
  pass

ESTRATEGIAS=(
  (2,_(u'PLM (Modelo Tiempo Contínuo) + Heurística basada en dependencias')),)

CLASES_ESTRATEGIAS={
  0: PlanificadorHagoLoQuePuedo,
  2: PlanificadorLinealContinuo, }

ESTADO_CRONOGRAMA_INVALIDO=0
ESTADO_CRONOGRAMA_VALIDO=1
ESTADO_CRONOGRAMA_ACTIVO=2
ESTADO_CRONOGRAMA_FINALIZADO=3
ESTADO_CRONOGRAMA_CANCELADO=4

ESTADOS_CRONOGRAMAS=(
  (ESTADO_CRONOGRAMA_INVALIDO,_(u'Inválido')),
  (ESTADO_CRONOGRAMA_VALIDO,_(u'Válido')),
  (ESTADO_CRONOGRAMA_ACTIVO,_(u'Activo')),
  (ESTADO_CRONOGRAMA_FINALIZADO,_(u'Finalizado')),
  (ESTADO_CRONOGRAMA_CANCELADO,_(u'Cancelado')),
  )

ESTADO_INTERVALO_PLANIFICADO=0
ESTADO_INTERVALO_ACTIVO=1
ESTADO_INTERVALO_FINALIZADO=2
ESTADO_INTERVALO_CANCELADO=3

ESTADOS_INTERVALOS=(
  (ESTADO_INTERVALO_PLANIFICADO,_(u'Planificado')),
  (ESTADO_INTERVALO_ACTIVO,_(u'Activo')),
  (ESTADO_INTERVALO_FINALIZADO,_(u'Finalizado')),
  (ESTADO_INTERVALO_CANCELADO,_(u'Cancelado')),
)

DICT_ESTADO_INTERVALO = dict(ESTADOS_INTERVALOS)

class PedidoYaDistribuido(ValidationError):
  pass

class CalendarioProduccion:

  @staticmethod
  def get_instance():
    try:
      return calendario.models.Calendario.objects.get()
    except calendario.models.Calendario.DoesNotExist:
      instance = calendario.models.Calendario()
      instance.clean()
      instance.save()
      return instance

class MaquinaPlanificacion(Maquina):

  class Meta:
    proxy = True
    app_label = 'planificacion'

  def get_calendario(self):
    return CalendarioProduccion.get_instance()

  def produce(self, tarea, producto):
    return self.tiemporealizaciontarea_set.filter(
      tarea=tarea,producto=producto, activa=True).count() > 0

  @staticmethod
  def fromMaquina(maquina):
    maquina.__class__ = MaquinaPlanificacion
    return maquina

  def get_intervalos_activos(self):
    return IntervaloCronograma.get_intervalos_activos(
        ).filter(maquina=self) 

  def get_intervalos(self):
    return IntervaloCronograma.objects.filter(maquina=self) 

class Cronograma(PlanificacionBaseModel):
  """
  Validar:
  - intervalo_tiempo no puede ser modificado en caso que existan instancias
  de IntervaloCronograma.
  """
  descripcion = models.CharField(max_length=100, verbose_name=_(u'Descripción'))
  fecha_inicio = models.DateTimeField( verbose_name=_(u'Fecha de inicio'), null=True, blank=True, default=tz_now)
  estrategia = models.IntegerField(verbose_name=_(u'Estrategia de planificación'), choices=ESTRATEGIAS, default=2)
  tiempo_minimo_intervalo = models.DecimalField(default=60,
    max_digits=8, decimal_places=2, verbose_name=_(u'Tiempo mínimo de cada intervalo (min)'), 
    help_text=_(u'Tiempo mínimo de cada intervalo que compone el cronograma. NO será tenido en cuenta durante la resolución del modelo lineal. Esto quiere decir que si la resolución del modelo lineal obtiene intervalos con tiempo menor al definido, estos serán incorporados al cronograma.'))
  optimizar_planificacion = models.BooleanField(default=True, verbose_name=(u'Optimizar planificación'),
    help_text=_(u'Una vez obtenida la planificación intenta optimizarla un poco más.'))
  estado = models.IntegerField(editable=False, verbose_name=_(u'Estado'),
    choices=ESTADOS_CRONOGRAMAS, default=ESTADO_CRONOGRAMA_INVALIDO)
  tolerancia = models.DecimalField(default=0.005,
    max_digits=3, decimal_places=3, verbose_name=_(u'Tolerancia a errores de planificación.'), 
    help_text=_(u'Tolerancia a errores de planificación. Indica el factor de tolerancia a los errores durante la planificación. Por ejemplo, un valor de 0.02 para un item de un pedido con cantidad 100, indica que puede haber un error de planificación de 2 unidades.'))
  _particionar_pedidos = models.BooleanField(default=True, verbose_name=(u'Particionar pedidos'),
    help_text=_(u'Seleccionando esta opción se estimará cuanto demora la fabricación de cada producto. '+
      u'Luego en función de la estimación se calculará el ideal de la cantidad de productos por item para '+
      u'aproximarse al tiempo de producción por item indicado.'))
  tiempo_produccion_por_item = models.DecimalField(default=40, max_digits=8, decimal_places=2,
      verbose_name=_(u'Tiempo de producción por item (horas)'), 
      help_text=_(u'Indica el tiempo de producción esperado por item en horas. Sirve para '+
        u'subdividir en forma automatica en varios items los productos de un pedido de forma de '+
        u'poder organizar mejor los lotes de producción y reducir notablemente los tiempos '+
        u'de planificación'))
  cantidad_extra_tarea_anterior = models.DecimalField(default=0, max_digits=8, decimal_places=2,
      verbose_name=_(u'Cantidad Extra en Tarea Anterior'), 
      help_text=_(u'Sean A y B dos tareas, donde A depende de B (B debe producirse antes que A). '+
          u'Este parámetro indica, si queremos planificar B, a partir de que instante '+
          u'puede planificarse en función de la cantidad que ya está producida de A. '+
          u'Por ejemplo, si esta cantidad es 2 y se quiere producir 50 de A y 50 de B, '+
          u'si hasta el instanet t1 tenemos planificado A(12) y B(10), y en hasta el instante '+
          u't2 tenemos planificado A(20) y B(10), entonces entre t1 y t2, podremos planificar '+
          u'una cantidad de 8 para B.'))


  class Meta:
    ordering = ['-id']
    verbose_name = _(u"Cronograma")
    verbose_name_plural = _(u"Cronogramas")
    app_label = 'planificacion'

  def estimar_tiempo_fabricacion_producto(self, producto):
    """
    Obtiene la estimacion del tiempo para producir una unidad 
    de producto con las mismas máquinas de self.
    La estimación es devuelta en segundos.
    """
 
    pedido = PedidoPlanificable.objects.create()
    pedido.add_item(producto,1)

    # Se utiliza una fecha de inicio sin sentido 1/1/1
    cronograma = pedido.crear_cronograma(fecha_inicio=tz_now(),
        _particionar_pedidos=False, tiempo_minimo_intervalo=30)

    # Eliminamos las máquinas del nuevo cronograma 
    # que no se encuentran en el cronograma actual.
    for maquinacronograma in cronograma.maquinacronograma_set.all():
      if not self.has_maquina(maquinacronograma.maquina):
        maquinacronograma.delete()

    cronograma.planificar()

    planificacion_desde = cronograma.get_intervalos(
        ).aggregate(Min('fecha_desde'))['fecha_desde__min']
    planificacion_hasta = cronograma.get_intervalos(
        ).aggregate(Max('fecha_hasta'))['fecha_hasta__max']

    calendario = CalendarioProduccion.get_instance()

    tiempo_efectivo_produccion = 0
    for hueco in calendario.get_huecos(desde=planificacion_desde,
        hasta=planificacion_hasta):
      tiempo_efectivo_produccion += hueco.get_segundos()

    cronograma.invalidar()
    cronograma.delete()
    pedido.delete()

    return tiempo_efectivo_produccion

  def crear_intervalo(self, maquina, tarea, item,
    fecha_desde, tiempo_intervalo):
    return IntervaloCronograma(
      cronograma=self, maquina=maquina, tarea=tarea, item=item, 
      fecha_desde=fecha_desde, tiempo_intervalo=tiempo_intervalo)

  def get_tolerancia(self, cantidad):
    return D(self.tolerancia) * D(cantidad)

  def get_gerenciador_dependencias(self, item):
    return GerenciadorDependencias(self, item)

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
    for maquina in MaquinaPlanificacion.objects.filter(id__in=posibles):
      if maquina.tareamaquina_set.filter(
        tarea__in=tareas_maquinas_restantes).count() == 0:
        result.add(maquina.id) 
    return result

  def is_maquina_cuello_botella(self, maquina):
    return maquina.id in self.get_ids_maquinas_cuello_botella()

  def has_maquina(self, maquina):
    try:
      self.maquinacronograma_set.get(cronograma=self,maquina=maquina)
      return True
    except MaquinaCronograma.DoesNotExist:
      pass
    return False

  def is_invalido(self):
    return self.estado == ESTADO_CRONOGRAMA_INVALIDO

  def is_valido(self):
    return self.estado == ESTADO_CRONOGRAMA_VALIDO

  def is_activo(self):
    return self.estado == ESTADO_CRONOGRAMA_ACTIVO

  def is_finalizado(self):
    return self.estado == ESTADO_CRONOGRAMA_FINALIZADO

  def particionar_pedidos(self):
    if not self._particionar_pedidos:
      return
    for pedido in self.get_pedidos():
      pedido.particionar_productos_optimizando(
          tiempo_de_realizacion_item_en_horas=self.tiempo_produccion_por_item,
          cronograma=self)

  @transaction.atomic
  def planificar(self):
    """
    Este es el core del producto. Acá es donde en función de la configuración 
    de producción y del cronograma se van a generar los intervalos del 
    cronograma con la planificación correspondiente para llevar a cabo la
    producción.
    """
    if not self.is_invalido():
      raise EstadoCronogramaError(_(u'El cronograma %s no se puede '+
        u'planificar ya que no se encuentra en un estado invalido.') % self)
    IntervaloCronograma.objects.filter(cronograma=self).delete()
    self.particionar_pedidos()
    planificador = CLASES_ESTRATEGIAS[self.estrategia](self)
    planificador.planificar()
    self.estado = ESTADO_CRONOGRAMA_VALIDO
    self.clean()
    self.save()
    cronograma_planificado.send(sender=self.__class__, instance=self)

  @transaction.atomic
  def invalidar(self, forzar=False):

    if forzar:
      self.estado = ESTADO_CRONOGRAMA_INVALIDO
      self.intervalocronograma_set.all().delete()
      self.save()
      return

    if not self.is_valido():
      raise EstadoCronogramaError(_(u'No se puede invalidar el cronograma %s, '+
        u'el mismo debe tener estado válido para invalidarlo.') % self)
    self.estado = ESTADO_CRONOGRAMA_INVALIDO
    self.save()
    self.intervalocronograma_set.all().delete()
    self.clean()
    self.save()

  @transaction.atomic
  def do_activar(self):
    self.estado = ESTADO_CRONOGRAMA_ACTIVO
    self.save()
    self.activar_intervalos()

  @transaction.atomic
  def activar(self):
    if not self.is_valido():
      raise EstadoCronogramaError(_(u'El cronograma %s no puede ser '
        u'activado. Para poder ser activado debe encontrarse en un estado válido.') % self)
    try:
        self.do_activar()
    except ValidationError:
        self.estado = ESTADO_CRONOGRAMA_VALIDO
        self.invalidar()
        self.planificar()
        self.do_activar()

  @transaction.atomic
  def desactivar(self):
    if not self.is_activo():
      raise EstadoCronogramaError(_(u'El cronograma %s no se encuentra activo.') % self)
    self.estado = ESTADO_CRONOGRAMA_VALIDO
    self.save()
    self.desactivar_intervalos()
    self.clean()
    self.save()

  @transaction.atomic
  def finalizar(self):
    if not self.is_activo():
      raise EstadoCronogramaError(_(u'El cronograma %s no se encuentra activo.') % self)
    self.estado = ESTADO_CRONOGRAMA_FINALIZADO
    self.save()
    self.finalizar_intervalos()
    self.clean()
    self.save()

  def get_intervalos_ordenados_por_dependencia(self, **filtros_adicionales):
    for pedido in self.get_pedidos():
      for item in pedido.get_items():
        for tarea in item.producto.get_tareas_ordenadas_por_dependencia():
          for intervalo in self.intervalocronograma_set.filter(
            item=item, tarea=tarea, **filtros_adicionales):
            yield intervalo

  def finalizar_intervalos(self):
    for intervalo in self.get_intervalos_ordenados_por_dependencia(
      estado=ESTADO_INTERVALO_ACTIVO):
      intervalo.finalizar()

  def desactivar_intervalos(self):
    for intervalo in self.intervalocronograma_set.all():
      intervalo.desactivar()

  def activar_intervalos(self):
    for intervalo in self.get_intervalos_ordenados_por_dependencia():
      intervalo.activar()

  @staticmethod
  def invalidar_cronogramas_validos():
    for cronograma in Cronograma.objects.filter(estado=ESTADO_CRONOGRAMA_VALIDO):
      cronograma.invalidar()

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
    for maquina in self.get_maquinas():
      if maquina.produce(tarea, producto):
        yield maquina

  def get_intervalos_activos_y_planificados(self):

    return IntervaloCronograma.objects.filter(
      cronograma=self).filter(estado__in=[
          ESTADO_INTERVALO_PLANIFICADO, ESTADO_INTERVALO_ACTIVO
          ])

  def get_intervalos_propios_no_cancelados(self):

    return IntervaloCronograma.objects.filter(
      cronograma=self).exclude(estado=ESTADO_INTERVALO_CANCELADO)

  def get_intervalos_activos_otros_cronogramas(self):

    return IntervaloCronograma.objects.filter(
      estado=ESTADO_INTERVALO_ACTIVO).exclude(
      cronograma=self)

  def get_intervalos_propios_y_activos(self, maquina=None):

    intervalos_propios = IntervaloCronograma.objects.filter(
      cronograma=self).exclude(estado=ESTADO_INTERVALO_CANCELADO)

    intervalos_activos = IntervaloCronograma.objects.filter(
      estado__in=[ESTADO_INTERVALO_ACTIVO, ESTADO_INTERVALO_FINALIZADO],
      fecha_hasta__gte=self.fecha_inicio)

    resultado = intervalos_propios | intervalos_activos

    if maquina is not None:
      resultado = resultado.filter(maquina=maquina)

    return resultado

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

  def remove_maquina(self, maquina):
    return self.maquinacronograma_set.filter(
        maquina=maquina).delete()

  def remove_pedido(self, pedido):
    return self.pedidocronograma_set.filter(
        pedido=pedido).delete()

  def add_maquina(self, maquina):
    return self.maquinacronograma_set.create(maquina=maquina)

  def add_pedido(self, pedido):
    return self.pedidocronograma_set.create(pedido=pedido)

  def validar_estado(self):
    if not self.is_activo() and not self.is_finalizado():

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

  def clean(self, *args, **kwargs):
    self.validar_estado()
    super(Cronograma, self).clean(*args, **kwargs)

class ItemPlanificable(ItemPedido):

    class Meta:
        proxy=True
        app_label = 'planificacion'

    def indice_planificacion(self):
        cantidades_planificadas_tareas = [
                self.get_cantidad_planificada(tarea) for tarea in self.producto.get_tareas() ]
        if len(cantidades_planificadas_tareas) == 0:
            return 0
        return ( D(sum(cantidades_planificadas_tareas)) /
                (D(len(cantidades_planificadas_tareas))*D(self.cantidad)) )

    def indice_finalizacion(self):
        cantidades_finalizadas_tareas = [
                self.get_cantidad_realizada(tarea) for tarea in self.producto.get_tareas() ]
        if len(cantidades_finalizadas_tareas) == 0:
            return 0
        return ( D(sum(cantidades_finalizadas_tareas)) /
                (D(len(cantidades_finalizadas_tareas))*D(self.cantidad)) )

    def get_cantidad_planificada(self, tarea):
        """
        Obtiene la cantidad de tarea planificada (ACTIVA) para el item
        en cuestion.
        """
        return IntervaloCronograma.get_cantidad_planificada(self, tarea)

    def get_cantidad_realizada(self, tarea, ids_intervalos_excluir=[]):
        return IntervaloCronograma.get_cantidad_realizada(self, tarea, ids_intervalos_excluir)

    def get_cantidad_no_planificada(self, tarea):
        return (self.cantidad - self.get_cantidad_realizada(tarea)
                - self.get_cantidad_planificada(tarea))

    def incrementarTareaReal(self, tarea, cantidad_tarea_real):
        try:
            tareaItem = TareaItem.objects.get(
                                              item=self,
                                              tarea=tarea)
            tareaItem.cantidad_realizada += cantidad_tarea_real
            tareaItem.save()
        except TareaItem.DoesNotExist:
            TareaItem(
                      item=self,
                      tarea=tarea,
                      cantidad_realizada=cantidad_tarea_real).save()

class TareaItem(PlanificacionBaseModel):
    
    item = models.ForeignKey(ItemPlanificable, verbose_name=_(u'Item'))
    tarea = models.ForeignKey(Tarea, verbose_name=_(u'Tarea'))
    
    """
    Acumula la cantidad realizada de tarea para el item en cuestión de
    forma de optimizar la consulta de tarea real realizada.
    Se debe actualizar cuando se finaliza un intervalo.
    """
    cantidad_realizada = models.DecimalField( default=0,
        max_digits=8, decimal_places=2, verbose_name=_(u'Cantidad Realizada'), 
        help_text=_(u'Cantidad de tarea realizada (real).'))



class PedidoPlanificable(Pedido):
  
  class Meta:
    proxy=True
    app_label = 'planificacion'

  def __unicode__(self):
    return unicode('#%s - %s' % (self.id, self.descripcion))

  def porcentaje_planificado(self):
      return self.indice_planificacion()*100

  def porcentaje_finalizado(self):
      return self.indice_finalizacion()*100

  def indice_planificacion(self):
      porcentajes_items = [ i.indice_planificacion() for i in self.get_items() ]
      if len(porcentajes_items) == 0:
          return 0
      return D(sum(porcentajes_items))/D(len(porcentajes_items))

  def indice_finalizacion(self):
      porcentajes_items = [ i.indice_finalizacion() for i in self.get_items() ]
      if len(porcentajes_items) == 0:
          return 0
      return D(sum(porcentajes_items))/D(len(porcentajes_items))

  @transaction.atomic
  def planificar_y_activar(self):
      cronograma = self.crear_cronograma()
      cronograma.planificar()
      cronograma.activar()

  def get_tolerancia(self):
      return 0.005

  def get_cronograma(self):
    return PedidoCronograma.objects.get(
        pedido=self).cronograma

  def crear_cronograma(self, fecha_inicio=None, **kwargs):
    if fecha_inicio is None:
        now = tz_now()
        fecha_inicio = now - TD(microseconds=now.microsecond) + TD(seconds=1)
    cronograma = Cronograma.objects.create(descripcion=
        _(u'Planificación del pedido #%s') % self.id, fecha_inicio=fecha_inicio,
        **kwargs)
    cronograma.add_pedido(self)
    return cronograma

  def planificar(self):
    try:
      cronograma = self.get_cronograma()
    except PedidoCronograma.DoesNotExist:
      cronograma = self.crear_cronograma()
    cronograma.planificar()

  def get_items(self):
    for i in ItemPlanificable.objects.filter(pedido=self):
      yield i

  def get_item_producto(self, producto):
    return ItemPlanificable.objects.get(
      pedido=self, producto=producto)

  def get_items_producto(self, producto):
    return ItemPlanificable.objects.filter(
      pedido=self, producto=producto)

  def get_maquinas_posibles_produccion(self):
    for maquina in super(PedidoPlanificable, self).get_maquinas_posibles_produccion():
      yield MaquinaPlanificacion.fromMaquina(maquina)

  def get_cronogramas(self):
    for pc in self.pedidocronograma_set.all():
      yield pc.cronograma

  def particionar(self, producto, cantidad_por_item):

    for item in self.get_items_producto(producto):
      if item.intervalocronograma_set.exists():
        raise ProductoConPlanificacionExistente(_(
          u'El item %s se encuentra asociado a uno o '+
          u'varios intervalos de planificación') % item)

    items = self.itempedido_set.filter(producto=producto)

    cantidad_items_producto = items.count()
    cantidad_productos = items.aggregate(
        cantidad_total=models.Sum('cantidad'))['cantidad_total']

    cantidad_por_item_actual = cantidad_productos / cantidad_items_producto

    if cantidad_por_item_actual <= cantidad_por_item:
      raise PedidoYaParticionado(_(u'Imposible particionar ya que la cantidad de productos '+
        'por item actual en promedio %s es menor que la solicitada %s.'))

    cantidad_items_esperados = int(cantidad_productos / cantidad_por_item)
    cantidad_ultimo_item = cantidad_productos % cantidad_por_item

    logger.debug(('Se particiona pedido %(pedido)s en %(cant_items)s '+
        'items de %(cant_productos)s.') % {
          'pedido': self,
          'cant_items': cantidad_items_esperados,
          'cant_productos': cantidad_por_item,
          })

    for item in items:
      item.cantidad = cantidad_por_item
      item.save()
      cantidad_items_esperados -= 1

    while cantidad_items_esperados > 0:
      self.itempedido_set.create(producto=producto, cantidad=cantidad_por_item)
      cantidad_items_esperados -= 1

    if cantidad_ultimo_item > 0:
      self.itempedido_set.create(producto=producto, cantidad=cantidad_ultimo_item)

  def get_cantidad_producto(self, producto):
    return self.get_items_producto(producto).aggregate(
        cantidad_total=models.Sum('cantidad'))['cantidad_total']

  def particionar_productos_optimizando(self,
      tiempo_de_realizacion_item_en_horas, cronograma=None):
    for producto in self.get_productos():
      try:
        self.particionar_optimizando(producto,
            tiempo_de_realizacion_item_en_horas,
            cronograma)
      except PedidoYaParticionado:
        pass
      except ProductoConPlanificacionExistente:
        pass

  def particionar_optimizando(self, producto,
      tiempo_de_realizacion_item_en_horas,
      cronograma=None):

    if cronograma is None:
      cronograma = self.get_cronograma()

    tiempo_fabricacion_producto_estimado = (
        cronograma.estimar_tiempo_fabricacion_producto(
          producto)
        )

    cantidad_producto_por_item = int( math.ceil(
        Decimal(tiempo_de_realizacion_item_en_horas * 3600) /
        Decimal(tiempo_fabricacion_producto_estimado) ) )

    self.particionar(producto, cantidad_producto_por_item)


class PedidoCronograma(PlanificacionBaseModel):
  cronograma = models.ForeignKey(Cronograma, verbose_name=_(u'Cronograma'))
  pedido = models.ForeignKey(PedidoPlanificable, verbose_name=_(u'Pedido'), on_delete=models.PROTECT)

  class Meta:
    ordering = ['pedido__descripcion']
    verbose_name = _(u"Pedido cronograma")
    verbose_name_plural = _(u"Pedidos cronograma")
    unique_together = (('cronograma', 'pedido'),)
    app_label = 'planificacion'

  def __unicode__(self):
    return self.pedido

class MaquinaCronograma(PlanificacionBaseModel):
  cronograma = models.ForeignKey(Cronograma, verbose_name=_(u'Cronograma'))
  maquina = models.ForeignKey(MaquinaPlanificacion, verbose_name=_(u'Máquina'), on_delete=models.PROTECT)

  class Meta:
    ordering = ['maquina__descripcion']
    verbose_name = _(u"Maquina cronograma")
    verbose_name_plural = _(u"Maquina cronograma")
    unique_together = (('cronograma', 'maquina'),)
    app_label = 'planificacion'

  def __unicode__(self):
    return self.maquina

class SolapamientoIntervalo(ValidationError):
  pass

class IntervaloAnteriorNoExiste(Exception):
  pass

class HuecoAdyacenteAnteriorNoExiste(Exception):
  pass


class IntervaloCronogramaManager(models.Manager):

  use_for_related_fields = True

  def exclude_cancelados(self):
    return IntervaloCronograma.objects.exclude(
      estado=ESTADO_INTERVALO_CANCELADO)


class IntervaloCronograma(PlanificacionBaseModel):

  objects = IntervaloCronogramaManager()

  cronograma = models.ForeignKey(Cronograma, verbose_name=_(u'Cronograma'))
  maquina = models.ForeignKey(MaquinaPlanificacion, verbose_name=_(u'Máquina'), on_delete=models.PROTECT)
  tarea = models.ForeignKey(Tarea, verbose_name=_(u'Tarea'), on_delete=models.PROTECT)
  cantidad_tarea = models.DecimalField( editable=False, default=0,
    max_digits=12, decimal_places=6, verbose_name=_(u'Cantidad Tarea Planificada'),
    help_text=_(u'Cantidad de tarea a producir en el intervalo.'))
  cantidad_tarea_real = models.DecimalField( default=0,
    max_digits=8, decimal_places=2, verbose_name=_(u'Cantidad Tarea Real'), 
    help_text=_(u'Cantidad de tarea producida (real).'))
  tiempo_intervalo = models.DecimalField(
    max_digits=12, decimal_places=6,
    verbose_name=_(u'Tiempo del intervalo (min)'))
  fecha_desde = models.DateTimeField(
    verbose_name=_(u'Fecha desde'), null=False, blank=False)
  fecha_hasta = models.DateTimeField(
    verbose_name=_(u'Fecha hasta'), null=True, blank=False)
  estado = models.IntegerField(editable=False, verbose_name=_(u'Estado'),
    choices=ESTADOS_INTERVALOS, default=0)
  item = models.ForeignKey(ItemPlanificable, editable=False, null=True, on_delete=models.CASCADE)

  # atributos exclusivos para asegurar la consistencia de la información
  tareamaquina = models.ForeignKey(TareaMaquina, editable=False, on_delete=models.PROTECT)
  tareaproducto = models.ForeignKey(TareaProducto, editable=False, on_delete=models.CASCADE)
  pedidocronograma = models.ForeignKey(PedidoCronograma, editable=False)
  maquinacronograma = models.ForeignKey(MaquinaCronograma, editable=False)

  # Atributos solo para usar en admin
  producto = models.ForeignKey(Producto, verbose_name=_(u'Producto'), editable=False, on_delete=models.PROTECT)
  pedido = models.ForeignKey(PedidoPlanificable, verbose_name=_(u'Pedido'), editable=False, on_delete=models.PROTECT)

  class Meta:
    ordering = ['-cronograma__id', 'fecha_desde']
    verbose_name = _(u"Intervalo cronograma")
    verbose_name_plural = _(u"Intervalos cronograma")
    unique_together = (('cronograma', 'maquina', 'fecha_desde'),)
    app_label = 'planificacion'

  def __unicode__(self):
    return '[#%s] [%s] [%s] [%s] [cant: %s] [%s]-[%s]' % (self.id,
      self.maquina.descripcion, self.tarea.descripcion, self.item,
      self.cantidad_tarea, self.get_fecha_desde().strftime('%Y-%m-%d %H:%M'),
      self.get_fecha_hasta().strftime('%Y-%m-%d %H:%M'))

  def __init__(self, *args, **kwargs):
      super(IntervaloCronograma, self).__init__(*args,**kwargs)
      if self.item is not None:
          self.producto = self.item.producto
          self.item.pedido.__class__ = PedidoPlanificable
          self.pedido = self.item.pedido

  @staticmethod
  def get_intervalos_modificables():
    return IntervaloCronograma.objects.filter(
      estado__in=[ESTADO_INTERVALO_ACTIVO,
        ESTADO_INTERVALO_PLANIFICADO])

  @staticmethod
  def get_intervalos_no_cancelados():
    return IntervaloCronograma.objects.exclude(
      estado=ESTADO_INTERVALO_CANCELADO)

  @staticmethod
  def get_intervalos_activos():
    return IntervaloCronograma.objects.filter(
      estado__in=[ESTADO_INTERVALO_ACTIVO,
        ESTADO_INTERVALO_FINALIZADO])

  @staticmethod
  def get_cantidad_planificada(item, tarea):
    """
    Obtiene la cantidad de tarea planificada (ACTIVA) para el item
    en cuestion.
    """
    total = IntervaloCronograma.objects.filter(
      tarea=tarea,
      item=item,
      estado=ESTADO_INTERVALO_ACTIVO
      ).aggregate(
        total=models.Sum('cantidad_tarea'))['total']
    if total is None:
      return 0
    else:
      return total

  @staticmethod
  def get_cantidad_realizada(item, tarea, ids_intervalos_excluir=[]):
    """
    Se obtiene la cantidad real de tarea realizada hasta el momento 
    para el item pasado. Lo ideal es obtener lo realizado hasta el momento de
    una sola consulta y restarle las cantidades reales de los intervalos a
    excluir.
    """
    
    try:
        tareaItem=TareaItem.objects.get(
                                 item=item,
                                 tarea=tarea)
        intervalos_a_excluir = IntervaloCronograma.objects.filter(
                                                            id__in=ids_intervalos_excluir)
        totalExcluir = intervalos_a_excluir.aggregate(
            total=models.Sum('cantidad_tarea_real'))['total']
            
        if totalExcluir is None:
            return tareaItem.cantidad_realizada
        else:
            return tareaItem.cantidad_realizada - totalExcluir
        
    except TareaItem.DoesNotExist:
        return 0
    
    intervalos_item = IntervaloCronograma.objects.filter(
      tarea=tarea,
      item=item,
      estado=ESTADO_INTERVALO_FINALIZADO
      ).exclude(id__in=ids_intervalos_excluir)
    total = intervalos_item.aggregate(total=models.Sum('cantidad_tarea_real'))['total']
    if total is None:
      return 0
    else:
      return total

  def get_descripcion_estado(self):
      return DICT_ESTADO_INTERVALO[self.estado]

  def get_duracion(self):
    """
    Obtiene un objeto datetime.timedelta
    """
    return self.fecha_hasta - self.fecha_desde

  @transaction.atomic
  def finalizar(self, cantidad_tarea_real=None):
    if cantidad_tarea_real is not None:
      self.cantidad_tarea_real = cantidad_tarea_real
    elif self.cantidad_tarea_real == 0:
      self.cantidad_tarea_real = self.cantidad_tarea
    self.estado = ESTADO_INTERVALO_FINALIZADO
    self.clean(validar_dependencias=False)

    self.save()

    item = self.getItem()
    item.incrementarTareaReal(self.tarea, self.cantidad_tarea_real)
    
    logger.info(_('Intervalo FINALIZADO: %s') % self)

  def is_planificado(self):
    return self.estado == ESTADO_INTERVALO_PLANIFICADO

  def is_activo(self):
    return self.estado == ESTADO_INTERVALO_ACTIVO

  def activar(self):
    if not self.is_planificado():
      raise EstadoIntervaloCronogramaError(
        _(u'El intervalo %s no tiene estado planificado.') % self)
    self.estado = ESTADO_INTERVALO_ACTIVO
    self.clean()
    self.save()

  def desactivar(self):
    if not self.is_activo():
      raise EstadoIntervaloCronogramaError(
        _(u'El intervalo %s no se encunetra activo') % self)
    self.estado = ESTADO_INTERVALO_PLANIFICADO
    self.clean()
    self.save()

  @transaction.atomic
  def cancelar(self, propagar=True):
    """
    Cancela el intervalo.
    Si propagar == True entonces cancela también los intervalos dependientes.
    Se verificará self.cancelado() == True
    """
    intervalos_cancelados = []
    if not self.is_activo():
      raise EstadoIntervaloCronogramaError(
        _(u'El intevalo %s no puede ser cancelado. El mismo no se encuentra activo.') % self)
    if propagar:
      for intervalo in reversed([ i for i in self.get_intervalos_dependientes() ]):
        intervalo.cancelar(propagar=False)
        intervalos_cancelados.append(intervalo)
    self.cantidad_tarea_real = 0
    self.estado = ESTADO_INTERVALO_CANCELADO
    self.clean(validar_dependencias=False)
    self.save()
    logger.info(_('Intervalo CANCELADO: %s') % self)
    intervalos_cancelados.append(self)
    return intervalos_cancelados

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
    return self.tarea.get_tiempo(self.maquina,self.item.producto)

  def get_intervalos_maquina(self):
    return self.cronograma.get_intervalos_maquina(self.maquina)

  def get_intervalos_dependientes(self):

    ids_tareas = set()

    for secuencia_dependencia in self.item.producto.get_listado_secuencias_dependencias():
      encontrada_self_tarea = False
      for tarea in secuencia_dependencia:
        if tarea.id == self.tarea.id:
          encontrada_self_tarea = True
        elif encontrada_self_tarea:
          ids_tareas.add(tarea.id)

    if len(ids_tareas) == 0:
      return

    for tarea in self.item.producto.get_tareas_ordenadas_por_dependencia():
      if tarea.id not in ids_tareas:
        continue
      for intervalo in IntervaloCronograma.objects.filter(
        tarea=tarea, item=self.item, estado=ESTADO_INTERVALO_ACTIVO):
        yield intervalo

  def calcular_fecha_desde(self):
    if self.fecha_desde:
      return
    intervalos = self.get_intervalos_maquina()
    if len(intervalos) == 0:
      self.fecha_desde = self.cronograma.fecha_inicio
    else:
      self.fecha_desde = intervalos.order_by('fecha_desde').last().get_fecha_hasta()

  def calcular_fecha_hasta(self):
#    self.fecha_hasta = self.get_fecha_desde() + datetime.timedelta(seconds=int(self.tiempo_intervalo*60))
    self.fecha_hasta = self.get_fecha_hasta()

  def get_fecha_desde(self):
    return self.fecha_desde

  def get_fecha_hasta(self):
    return self.get_fecha_desde() + datetime.timedelta(seconds=int(self.tiempo_intervalo*60))
  """
    if self.fecha_hasta is None:
      self.calcular_fecha_hasta()
    return self.fecha_hasta
    """

  def calcular_cantidad_tarea(self):
    if self.cantidad_tarea:
      return
    self.cantidad_tarea = Decimal(self.tiempo_intervalo) / Decimal(
      self.tarea.get_tiempo(self.maquina,self.item.producto))

  def validar_solapamiento(self):
    # TODO Analizar una posible mejora de performance
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

  #@profile
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

    if not self.is_finalizado():
      return

    if self.cantidad_tarea_real > 0:
      cantidades_reales_tareas = {}
      for listado_dependencias in self.getItem(
        ).producto.get_listado_secuencias_dependencias():
        tarea_anterior = None
        for tarea in listado_dependencias:
          if not tarea.id in cantidades_reales_tareas:
            cantidades_reales_tareas[tarea.id] = self.getItem(
              ).get_cantidad_realizada(tarea,[self.id])
            #cantidades_reales_tareas[tarea.id] = self.cronograma.get_cantidad_real_tarea(
              #tarea, ids_intervalos_excluir=[self.id]) 
            if tarea.id == self.tarea.id:
              cantidades_reales_tareas[tarea.id] += self.cantidad_tarea_real
          if tarea_anterior is not None:
            logger.debug('Cantidad tarea anterior: %s (%s); Cantidad tarea dependiente: %s (%s).' %
                      (cantidades_reales_tareas[tarea_anterior.id], tarea_anterior,
                      cantidades_reales_tareas[tarea.id], tarea))
            if (cantidades_reales_tareas[tarea.id] - cantidades_reales_tareas[tarea_anterior.id] >
                    self.cronograma.get_tolerancia(cantidades_reales_tareas[tarea.id]) ):
              raise TareaRealNoRespetaDependencias(_(u'La cantidad real %s de la tarea %s '+
                u'no puede superar la cantidad %s de la tarea %s de la cual '+
                u'depende.') % (cantidades_reales_tareas[tarea.id], tarea,
                cantidades_reales_tareas[tarea_anterior.id], tarea_anterior))
          tarea_anterior = tarea

  def validar_cantidad_real(self):
    if self.cantidad_tarea_real > 0:
      # Se verifica estado del cronograma para poder asignar cantidad real.
      if not self.cronograma.is_activo() and not self.cronograma.is_finalizado():
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
    return self.estado == ESTADO_INTERVALO_ACTIVO

  def validar_estado(self):
    if self.id:
      self_in_db = IntervaloCronograma.objects.get(pk=self.id)
      if self_in_db.is_finalizado():
        raise EstadoIntervaloCronogramaError(_(u'El intervalo %s '+
          u'no puede ser modificado ya que su estado es finalizado.') % 
          self_in_db)
      elif self_in_db.is_cancelado():
        raise EstadoIntervaloCronogramaError(_(u'El intervalo %s '+
          u'no puede ser modificado ya que su estado es cancelado.') % 
          self_in_db)

    if not self.cronograma.is_activo() and not self.cronograma.is_finalizado():

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

  def getItem(self):
    return self.item

  #@profile
  def clean(self, validar_dependencias=True, *args, **kwargs):
    self.tareamaquina = TareaMaquina.objects.get(tarea=self.tarea,maquina=self.maquina)
    self.tareaproducto = TareaProducto.objects.get(tarea=self.tarea,producto=self.item.producto)
    self.pedidocronograma = PedidoCronograma.objects.get(pedido=self.item.pedido,cronograma=self.cronograma)
    self.maquinacronograma = MaquinaCronograma.objects.get(maquina=self.maquina,cronograma=self.cronograma)
    self.calcular_fecha_desde()
    self.calcular_cantidad_tarea()
    self.calcular_fecha_hasta()
    self.validar_estado()
    self.validar_cantidad_real()
    self.validar_solapamiento()
    if validar_dependencias:
        self.validar_dependencias_guardado()
    self.validar_fecha_inicio_cronograma()
    super(IntervaloCronograma, self).clean(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.validar_dependencias_borrado()
    super(IntervaloCronograma, self).delete(*args, **kwargs) 

  def save(self, *args, **kwargs):
    super(IntervaloCronograma, self).save(*args, **kwargs) 
