# coding=utf-8
from calendario.models import Calendario

class CalendarioProduccion:

  @staticmethod
  def get_instance():
    try:
      return Calendario.objects.get()
    except Calendario.DoesNotExist:
      instance = Calendario()
      instance.clean()
      instance.save()
      return instance


