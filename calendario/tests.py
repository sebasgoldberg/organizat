# coding=utf-8
from django.test import TestCase
from datetime import time as T
from datetime import datetime as DT
from calendario.models import *
from django.utils.translation import ugettext as _
import datetime
from django.utils import timezone

def datetimezone(*args, **kwargs):
  return timezone.make_aware(
    datetime.datetime(*args), timezone.get_default_timezone())

DT = datetimezone

class CalendarioTestCase(TestCase):

  def test_24x7(self):

    calendario = Calendario()
    calendario.clean()
    calendario.save()

    # Domingo
    fecha_desde = DT(2014,6,8,22,30)

    self.assertTrue(calendario.is_24x7())

    # Se agrega un feriado el lunes 9/6/2014.
    calendario.add_excepcion_no_laborable(fecha=DT(2014,6,9))

    huecos = [ hueco for hueco in calendario.get_huecos(
      desde=fecha_desde, tiempo_total=TD(seconds=60*60*3)) ]

    self.assertEqual(len(huecos),2)
    self.assertEqual(huecos[0].fecha_desde, fecha_desde)
    self.assertEqual(huecos[0].get_fecha_hasta(), DT(2014,6,9))
    self.assertEqual(huecos[1].fecha_desde, DT(2014,6,9,23,59))
    self.assertEqual(huecos[1].get_fecha_hasta(), DT(2014,6,10,1,29))
 
 
  def test_calendario(self):

    calendario = Calendario()
    calendario.clean()
    calendario.save()

    # jueves
    fecha_desde = DT(2014,6,5,12,30)
    # martes
    fecha_hasta = DT(2014,6,10,13,45)

    self.assertTrue(calendario.is_24x7())

    huecos = [ hueco for hueco in calendario.get_huecos(
      desde=fecha_desde, hasta=fecha_hasta) ]

    self.assertEqual(len(huecos),1)
    hueco = huecos[0]
    self.assertEqual(hueco.fecha_desde, fecha_desde)
    self.assertEqual(hueco.get_fecha_hasta(), fecha_hasta)

    # se define calendario lu a vi de 8 a 12
    calendario.add_intervalos_laborables(
      dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES,
        DiaSemana.MIERCOLES,DiaSemana.JUEVES,DiaSemana.VIERNES],
      hora_desde=T(8), hora_hasta=T(12))

    self.assertFalse(calendario.is_24x7())

    huecos = [ hueco for hueco in calendario.get_huecos(
      desde=fecha_desde, hasta=fecha_hasta) ]

    self.assertEqual(len(huecos),3)
    self.assertEqual(huecos[0].fecha_desde, DT(2014,6,6,8))
    self.assertEqual(huecos[0].get_fecha_hasta(), DT(2014,6,6,12))
    self.assertEqual(huecos[1].fecha_desde, DT(2014,6,9,8))
    self.assertEqual(huecos[1].get_fecha_hasta(), DT(2014,6,9,12))
    self.assertEqual(huecos[2].fecha_desde, DT(2014,6,10,8))
    self.assertEqual(huecos[2].get_fecha_hasta(), DT(2014,6,10,12))

    # se redefine calendario lu a vi de 8 a 12 y de 13 a 17
    calendario.add_intervalos_laborables(
      dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES,
        DiaSemana.MIERCOLES,DiaSemana.JUEVES,DiaSemana.VIERNES],
      hora_desde=T(13),hora_hasta=T(17))

    self.assertFalse(calendario.is_24x7())

    huecos = [ hueco for hueco in calendario.get_huecos(
      desde=fecha_desde, hasta=fecha_hasta) ]

    self.assertEqual(len(huecos),7)

    self.assertEqual(huecos[0].fecha_desde, DT(2014,6,5,13))
    self.assertEqual(huecos[0].get_fecha_hasta(), DT(2014,6,5,17))

    self.assertEqual(huecos[1].fecha_desde, DT(2014,6,6,8))
    self.assertEqual(huecos[1].get_fecha_hasta(), DT(2014,6,6,12))
    self.assertEqual(huecos[2].fecha_desde, DT(2014,6,6,13))
    self.assertEqual(huecos[2].get_fecha_hasta(), DT(2014,6,6,17))

    self.assertEqual(huecos[3].fecha_desde, DT(2014,6,9,8))
    self.assertEqual(huecos[3].get_fecha_hasta(), DT(2014,6,9,12))
    self.assertEqual(huecos[4].fecha_desde, DT(2014,6,9,13))
    self.assertEqual(huecos[4].get_fecha_hasta(), DT(2014,6,9,17))

    self.assertEqual(huecos[5].fecha_desde, DT(2014,6,10,8))
    self.assertEqual(huecos[5].get_fecha_hasta(), DT(2014,6,10,12))

    self.assertEqual(huecos[6].fecha_desde, DT(2014,6,10,13))
    self.assertEqual(huecos[6].get_fecha_hasta(), fecha_hasta)

    # se agrega un día de trabajo el sábado 7/6/2014 de 9 a 13
    calendario.add_excepcion_laborable(fecha=DT(2014,6,7),
      hora_desde=T(9), hora_hasta=T(13))

    self.assertFalse(calendario.is_24x7())

    huecos = [ hueco for hueco in calendario.get_huecos(
      desde=fecha_desde, hasta=fecha_hasta) ]

    self.assertEqual(len(huecos),8)

    self.assertEqual(huecos[3].fecha_desde, DT(2014,6,7,9))
    self.assertEqual(huecos[3].get_fecha_hasta(), DT(2014,6,7,13))

    # Se agrega un feriado el lunes 9/6/2014.
    calendario.add_excepcion_no_laborable(fecha=DT(2014,6,9))

    huecos = [ hueco for hueco in calendario.get_huecos(
      desde=fecha_desde, hasta=fecha_hasta) ]

    self.assertEqual(len(huecos),6)

    self.assertEqual(huecos[3].fecha_desde, DT(2014,6,7,9))
    self.assertEqual(huecos[3].get_fecha_hasta(), DT(2014,6,7,13))

    self.assertEqual(huecos[4].fecha_desde, DT(2014,6,10,8))
    self.assertEqual(huecos[4].get_fecha_hasta(), DT(2014,6,10,12))

    # Se agrega una excepción laborable el martes 10/6/2014 entre las 
    # 7:00 y las 9:00
    calendario.add_excepcion_laborable(fecha=DT(2014,6,10),
      hora_desde=T(7), hora_hasta=T(9))

    huecos = [ hueco for hueco in calendario.get_huecos(
      desde=fecha_desde, hasta=fecha_hasta) ]

    self.assertEqual(len(huecos),6)

    self.assertEqual(huecos[4].fecha_desde, DT(2014,6,10,7))
    self.assertEqual(huecos[4].get_fecha_hasta(), DT(2014,6,10,12))

    # Se agrega una excepción laborable el martes 10/6/2014 entre las 
    # 12:00 y las 13:30
    calendario.add_excepcion_laborable(fecha=DT(2014,6,10),
      hora_desde=T(12), hora_hasta=T(13,30))

    huecos = [ hueco for hueco in calendario.get_huecos(
      desde=fecha_desde, hasta=fecha_hasta) ]

    self.assertEqual(len(huecos),5)

    self.assertEqual(huecos[4].fecha_desde, DT(2014,6,10,7))
    self.assertEqual(huecos[4].get_fecha_hasta(), fecha_hasta)

    # Se verifica el funcionamiento de la obtención de huecos
    # pasando el tiempo total
    huecos = [ hueco for hueco in calendario.get_huecos(
      desde=fecha_desde, tiempo_total=TD(seconds=60*60*10)) ]

    self.assertEqual(huecos[0].fecha_desde, DT(2014,6,5,13))
    self.assertEqual(huecos[0].get_fecha_hasta(), DT(2014,6,5,17))

    self.assertEqual(huecos[1].fecha_desde, DT(2014,6,6,8))
    self.assertEqual(huecos[1].get_fecha_hasta(), DT(2014,6,6,12))
    self.assertEqual(huecos[2].fecha_desde, DT(2014,6,6,13))
    self.assertEqual(huecos[2].get_fecha_hasta(), DT(2014,6,6,15))


  def test_intervalo_laborable(self):
    
    calendario = Calendario()
    calendario.clean()
    calendario.save()

    try:
      calendario.add_intervalo_laborable(DiaSemana.LUNES,
        hora_desde=T(16), hora_hasta=T(12))
      self.fail(_(u'La hora desde debe ser menor que la hora hasta.'))
    except HoraDesdeMayorHoraHasta:
      pass

    calendario.add_intervalo_laborable(DiaSemana.LUNES,
      hora_desde=T(12), hora_hasta=T(16))

    try:
      calendario.add_intervalo_laborable(DiaSemana.LUNES,
        hora_desde=T(12), hora_hasta=T(16))
      self.fail(_(u'No debería permitir solapar intervalos laborables.'))
    except SolapamientoIntervalosLaborales:
      pass

    try:
      calendario.add_intervalo_laborable(DiaSemana.LUNES,
        hora_desde=T(11), hora_hasta=T(13))
      self.fail(_(u'No debería permitir solapar intervalos laborables.'))
    except SolapamientoIntervalosLaborales:
      pass

    try:
      calendario.add_intervalo_laborable(DiaSemana.LUNES,
        hora_desde=T(15), hora_hasta=T(17))
      self.fail(_(u'No debería permitir solapar intervalos laborables.'))
    except SolapamientoIntervalosLaborales:
      pass

    try:
      calendario.add_intervalo_laborable(DiaSemana.LUNES,
        hora_desde=T(11), hora_hasta=T(17))
      self.fail(_(u'No debería permitir solapar intervalos laborables.'))
    except SolapamientoIntervalosLaborales:
      pass

    try:
      calendario.add_intervalo_laborable(DiaSemana.LUNES,
        hora_desde=T(14), hora_hasta=T(15))
      self.fail(_(u'No debería permitir solapar intervalos laborables.'))
    except SolapamientoIntervalosLaborales:
      pass

    calendario.add_intervalo_laborable(DiaSemana.LUNES,
      hora_desde=T(7), hora_hasta=T(11))

  def test_excepcion_laborable(self):
    
    calendario = Calendario()
    calendario.clean()
    calendario.save()

    try:
      calendario.add_excepcion_laborable(DT(2014,1,2),T(18),T(12))
      self.fail(_(u'La fecha desde no debería ser mayor que la fecha hasta.'))
    except HoraDesdeMayorHoraHasta:
      pass

    try:
      calendario.add_excepcion_no_laborable(DT(2014,1,2),T(18),T(12))
      self.fail(_(u'La fecha desde no debería ser mayor que la fecha hasta.'))
    except HoraDesdeMayorHoraHasta:
      pass

    calendario.add_excepcion_laborable(DT(2014,2,1),T(12),T(18))

    try:
      calendario.add_excepcion_laborable(DT(2014,2,1),T(12),T(18))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_no_laborable(DT(2014,2,1),T(12),T(18))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_laborable(DT(2014,2,1),T(11),T(19))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_no_laborable(DT(2014,2,1),T(11),T(19))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_laborable(DT(2014,2,1),T(11),T(16))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_no_laborable(DT(2014,2,1),T(11),T(16))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_laborable(DT(2014,2,1),T(13),T(17))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_no_laborable(DT(2014,2,1),T(13),T(17))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_laborable(DT(2014,2,1),T(14),T(19))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_no_laborable(DT(2014,2,1),T(14),T(19))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    calendario.add_excepcion_no_laborable(DT(2014,2,1),T(6),T(11))

  def test_multiples_excepciones_no_laborables(self):

    calendario = Calendario.objects.create()

    calendario.add_intervalos_laborables(
      dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES,
        DiaSemana.MIERCOLES,DiaSemana.JUEVES,DiaSemana.VIERNES],
      hora_desde=T(8), hora_hasta=T(12))

    calendario.add_intervalos_laborables(
      dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES,
        DiaSemana.MIERCOLES,DiaSemana.JUEVES,DiaSemana.VIERNES],
      hora_desde=T(13),hora_hasta=T(17))

    calendario.add_excepcion_no_laborable(DT(2014,8,5),T(0),T(23))
    calendario.add_excepcion_no_laborable(DT(2014,9,16),T(0),T(23))
