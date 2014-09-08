# coding=utf-8
from django.utils.translation import ugettext_lazy as _
from decimal import Decimal as D
from django.utils import timezone as TZ

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
    return D(self.tiempo.total_seconds()) / 60

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


