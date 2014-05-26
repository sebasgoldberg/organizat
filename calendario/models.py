# coding=utf-8
from django.db import models
from django.utils.translation import ugettext as _
from planificacion.models import Hueco
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime as DT
from datetime import timedelta as TD
from datetime import time as T

class SolapamientoIntervalosLaborales(ValidationError):

  def __init__(self):
    super(SolapamientoIntervalosLaborales,self).__init__(
      _(u'No puede existir solapamiento entre intervalos laborales.'))

class HoraDesdeMayorHoraHasta(ValidationError):

  def __init__(self):
    super(HoraDesdeMayorHoraHasta,self).__init__(
      _(u'La hora desde debe ser menor que la hora hasta.'))

class SolapamientoExcepcionesLaborales(ValidationError):

  def __init__(self):
    super(SolapamientoExcepcionesLaborales,self).__init__(
      _(u'No puede existir solapamiento entre excepciones laborales.'))

class DiaSemana:
  LUNES=0
  MARTES=1
  MIERCOLES=2
  JUEVES=3
  VIERNES=4
  SABADO=5
  DOMINGO=6

DIAS_SEMANA=(
  (DiaSemana.LUNES,_(u'Lunes')),
  (DiaSemana.MARTES,_(u'Martes')),
  (DiaSemana.MIERCOLES,_(u'Miércoles')),
  (DiaSemana.JUEVES,_(u'Jueves')),
  (DiaSemana.VIERNES,_(u'Viernes')),
  (DiaSemana.SABADO,_(u'Sábado')),
  (DiaSemana.DOMINGO,_(u'Domingo')),)

def datetime_desde_fecha_hora(fecha, hora):
  return DT(fecha.year, fecha.month, fecha.day,
      hora.hour, hora.minute, hora.second)

class Calendario(models.Model):

  @staticmethod
  def get_instance():
    instance = None
    try:
      instance = Calendario.objects.first()
    except Calendario.DoesNotExists:
      pass
    if not instance:
      instance = Calendario()
      instance.clean()
      instance.save()
    return instance

  def is_24x7(self):
    return self.intervalolaborable_set.count() == 0
    
  def get_huecos_24x7(self, desde, hasta):

    if desde.date() == hasta.date():
      excepciones_no_laborables = self.excepcionlaborable_set.filter(
        fecha=desde.date(), hora_hasta__gte=desde.time(),
        hora_desde__lte=hasta.time(), laborable=False
        ).order_by('fecha', 'hora_desde')
    else:
      excepciones_no_laborables = (
        self.excepcionlaborable_set.filter(
        fecha=desde.date(), hora_hasta__gte=desde.time(),
        laborable=False) |
        self.excepcionlaborable_set.filter(
        fecha__gt=desde.date(), fecha__lt=hasta.date(),
        laborable=False) |
        self.excepcionlaborable_set.filter(
        fecha=hasta.date(), hora_hasta__lte=hasta.time(),
        laborable=False) 
        ).order_by('fecha', 'hora_desde')

    excepcion_anterior = None
    fecha_desde = desde
    for excepcion_no_laborable in excepciones_no_laborables:
      if excepcion_anterior is None:
        if excepcion_no_laborable.get_fecha_desde() < desde:
          fecha_desde = excepcion_no_laborable.get_fecha_hasta()
      else:
        yield Hueco(fecha_desde,
          fecha_hasta=excepcion_no_laborable.get_fecha_desde())
        fecha_desde = excepcion_no_laborable.get_fecha_hasta()
      excepcion_anterior = excepcion_no_laborable
    if fecha_desde < hasta:
      yield Hueco(fecha_desde, fecha_hasta=hasta)

  def get_huecos_dia(self, fecha):
    intervalos = self.intervalolaborable_set.filter(
      dia=fecha.weekday()).order_by('hora_desde')

    for intervalo in intervalos:
      for h in intervalo.get_huecos(fecha):
        yield h

  def get_huecos_dia_desde_hora(self, fecha, hora_desde):
    for h in self.get_huecos_dia(fecha):
      if h.fecha_desde.time() > hora_desde:
        yield h
      elif h.get_fecha_hasta().time() > hora_desde:
        yield Hueco(datetime_desde_fecha_hora(fecha, hora_desde),
          fecha_hasta=h.get_fecha_hasta())

  def get_huecos_dia_hasta_hora(self, fecha, hora_hasta):
    for h in self.get_huecos_dia(fecha):
      if h.get_fecha_hasta().time() < hora_hasta:
        yield h
      elif h.fecha_desde.time() < hora_hasta:
        yield Hueco(h.fecha_desde,
          fecha_hasta=datetime_desde_fecha_hora(fecha, hora_hasta))

  def get_huecos_no_24x7(self, desde, hasta):
    fecha_desde = desde.date()
    fecha_hasta = hasta.date()
    fecha = fecha_desde
    while fecha <= fecha_hasta:
      if fecha == fecha_desde:
        for h in self.get_huecos_dia_desde_hora(fecha, desde.time()):
          yield h
      elif fecha == fecha_hasta:
        for h in self.get_huecos_dia_hasta_hora(fecha, hasta.time()):
          yield h
      else:
        for h in self.get_huecos_dia(fecha):
          yield h
      fecha = fecha + TD(days=1)


  def get_huecos(self, desde, hasta):
    """
    Obtiene los intervalos laborables entre la fecha desde y la fecha hasta.
    """
    if self.is_24x7(): 
      for h in self.get_huecos_24x7(desde, hasta):
        yield h
    else:
      for h in self.get_huecos_no_24x7(desde, hasta):
        yield h

  @transaction.atomic
  def add_intervalos_laborables(self, dias_laborables, hora_desde, hora_hasta):
    for dia in dias_laborables:
      self.add_intervalo_laborable(dia, hora_desde, hora_hasta)

  def add_intervalo_laborable(self, dia, hora_desde, hora_hasta):
    intervalo = IntervaloLaborable(calendario=self, dia=dia, 
      hora_desde=hora_desde, hora_hasta=hora_hasta)
    intervalo.clean()
    intervalo.save()

  def add_excepcion_laborable(self, fecha, hora_desde=T(0), hora_hasta=T(23,59)):
    el = ExcepcionLaborable(calendario=self, 
      fecha=fecha, hora_desde=hora_desde, hora_hasta=hora_hasta,
      laborable=True)
    el.clean()
    el.save()
    return el

  def add_excepcion_no_laborable(self, fecha, hora_desde=T(0), hora_hasta=T(23,59)):
    el = ExcepcionLaborable(calendario=self, 
      fecha=fecha, hora_desde=hora_desde, hora_hasta=hora_hasta,
      laborable=False)
    el.clean()
    el.save()
    return el

class IntervaloLaborable(models.Model):
  
  calendario = models.ForeignKey(Calendario, verbose_name=_(u'Calendario'))
  dia = models.IntegerField(verbose_name=_(u'Día'), choices=DIAS_SEMANA)
  hora_desde = models.TimeField(verbose_name=_(u'Hora desde'))
  hora_hasta = models.TimeField(verbose_name=_(u'Hora hasta'))

  def clean(self):
    """
    No puede haber solapamiento en un mismo calendario.
    """
    if self.hora_desde >= self.hora_hasta:
      raise HoraDesdeMayorHoraHasta()

    if self.calendario.intervalolaborable_set.filter(dia=self.dia,
      hora_desde__lte=self.hora_desde, 
      hora_hasta__gte=self.hora_desde).count()>0:
      raise SolapamientoIntervalosLaborales()

    if self.calendario.intervalolaborable_set.filter(dia=self.dia,
      hora_desde__lte=self.hora_hasta, 
      hora_hasta__gte=self.hora_hasta).count()>0:
      raise SolapamientoIntervalosLaborales()

    if self.calendario.intervalolaborable_set.filter(dia=self.dia,
      hora_desde__gte=self.hora_desde, 
      hora_desde__lte=self.hora_hasta).count()>0:
      raise SolapamientoIntervalosLaborales()

    if self.calendario.intervalolaborable_set.filter(dia=self.dia,
      hora_hasta__gte=self.hora_desde, 
      hora_hasta__lte=self.hora_hasta).count()>0:
      raise SolapamientoIntervalosLaborales()

  def get_huecos(self, fecha):

    no_laborables = self.calendario.excepcionlaborable_set.filter(
      laborable=False, fecha=fecha)

    hora_desde = self.hora_desde
    hora_hasta = self.hora_hasta

    if no_laborables.filter(hora_desde__lte=hora_desde,
      hora_hasta__gte=hora_hasta).count() > 0:
      return

    no_laborables_hora_desde = no_laborables.filter(
      hora_desde__lte=hora_desde, hora_hasta__gte=hora_desde)
    if no_laborables_hora_desde.count() > 0:
      hora_desde = no_laborables_hora_desde[0].hora_hasta

    no_laborables_hora_hasta= no_laborables.filter(
      hora_desde__lte=hora_hasta, hora_hasta__gte=hora_hasta)
    if no_laborables_hora_hasta.count() > 0:
      hora_hasta = no_laborables_hora_desde[0].hora_desde

    no_laborables_interior = no_laborables.filter(
      hora_desde__gte=hora_desde, hora_hasta__lte=hora_hasta)

    for excepcion in no_laborables_interior:
      yield Hueco(datetime_desde_fecha_hora(fecha,hora_desde),
        fecha_hasta=datetime_desde_fecha_hora(excepcion.fecha,
          excepcion.hora_desde))
      hora_desde = excepcion.hora_hasta

    if hora_desde < hora_hasta:
      yield Hueco(datetime_desde_fecha_hora(fecha, hora_desde),
        fecha_hasta=datetime_desde_fecha_hora(fecha, hora_hasta))

class ExcepcionLaborable(models.Model):
  
  calendario = models.ForeignKey(Calendario, verbose_name=_(u'Calendario'))
  fecha = models.DateField(
    verbose_name=_(u'Fecha'), null=False, blank=False)
  hora_desde = models.TimeField(verbose_name=_(u'Hora desde'))
  hora_hasta = models.TimeField(verbose_name=_(u'Hora hasta'))
  laborable = models.BooleanField(verbose_name=(u'Laborable'),
    help_text=_(u'Indica si la excepción es laborable o no laborable.'),
    default=False)

  def clean(self):

    if self.hora_desde >= self.hora_hasta:
      raise HoraDesdeMayorHoraHasta()

    if self.calendario.excepcionlaborable_set.filter(fecha=self.fecha,
      hora_desde__lte=self.hora_desde, 
      hora_hasta__gte=self.hora_desde).count()>0:
      raise SolapamientoExcepcionesLaborales()

    if self.calendario.excepcionlaborable_set.filter(fecha=self.fecha,
      hora_desde__lte=self.hora_hasta, 
      hora_hasta__gte=self.hora_hasta).count()>0:
      raise SolapamientoExcepcionesLaborales()

    if self.calendario.excepcionlaborable_set.filter(fecha=self.fecha,
      hora_desde__gte=self.hora_desde, 
      hora_desde__lte=self.hora_hasta).count()>0:
      raise SolapamientoExcepcionesLaborales()

    if self.calendario.excepcionlaborable_set.filter(fecha=self.fecha,
      hora_hasta__gte=self.hora_desde, 
      hora_hasta__lte=self.hora_hasta).count()>0:
      raise SolapamientoExcepcionesLaborales()


