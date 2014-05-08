from django.db import models

class IntervaloLaborable(models.Model):
  
  dia_desde = None
  dia_hasta = None
  hora_desde = None
  hora_hasta = None

class ExcepcionLaborable(models.Model):
  
  fecha_desde = None
  fecha_hasta = None
  hora_desde = None
  hora_hasta = None

class Calendario(models.Model):

  intervalos_laborables = None
  excepciones_no_laborables = None
  excepciones_laborables = None

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
  
  def get_intervalo_laboral(self, fecha):
    """
    Obtiene el intervalo laboral en el que se encuentra la fecha pasada.
    Si la fecha no se encuentra dentro de un intervalo laboral, entonces
    Se arroja un excepción del tipo ValidationError
    """

  def validar_in_intervalo_laboral(self, intervalo):
    intervalo_laboral_fecha_desde = self.get_intervalo_laboral(intervalo.get_fecha_desde())
    intervalo_laboral_fecha_hasta = self.get_intervalo_laboral(intervalo.get_fecha_hasta())
    if not intervalo_laboral_fecha_desde.get_fecha_desde() ==\
      intervalo_laboral_fecha_hasta.get_fecha_desde():
      raise ValidationError(_(u'La fecha inicial y final del intervalo %s se '+
        u'encuentran en intervalos laborales distintos: %s y %s.') % (
        intervalo, intervalo_laboral_fecha_desde,
        intervalo_laboral_fecha_hasta))

