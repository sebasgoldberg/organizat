# coding=utf-8
from django.test import TestCase
from datetime import time as T
from datetime import datetime as DT
from calendario.models import *
from django.utils.translation import ugettext as _

class CalendarioTestCase(TestCase):

  def test_calendario(self):

    calendario = Calendario()
    calendario.clean()
    calendario.save()

    fecha_desde = DT(2014,6,5,12,30)
    fecha_hasta = DT(2014,6,10,13,45)

    self.assertTrue(calendario.is_24x7())

    huecos = [ hueco for hueco in calendario.get_huecos(
      desde=fecha_desde, hasta=fecha_hasta) ]

    self.assertEqual(len(huecos),1)
    hueco = huecos[0]
    self.assertEqual(hueco.fecha_desde, fecha_desde)
    self.assertEqual(hueco.get_fecha_hasta(), fecha_hasta)

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

    calendario.add_excepcion_laborable(fecha=DT(2014,6,7),
      hora_desde=T(9), hora_hasta=T(13))

    self.assertFalse(calendario.is_24x7())

    huecos = [ hueco for hueco in calendario.get_huecos(
      desde=fecha_desde, hasta=fecha_hasta) ]

    self.assertEqual(len(huecos),8)

    self.assertEqual(huecos[3].fecha_desde, DT(2014,6,7,9))
    self.assertEqual(huecos[3].get_fecha_hasta(), DT(2014,6,7,13))

    calendario.add_excepcion_no_laborable(fecha=DT(2014,6,9))

    huecos = [ hueco for hueco in calendario.get_huecos(
      desde=fecha_desde, hasta=fecha_hasta) ]

    self.assertEqual(len(huecos),6)

    self.assertEqual(huecos[3].fecha_desde, DT(2014,6,7,9))
    self.assertEqual(huecos[3].get_fecha_hasta(), DT(2014,6,7,13))

    self.assertEqual(huecos[4].fecha_desde, DT(2014,6,10,8))
    self.assertEqual(huecos[4].get_fecha_hasta(), DT(2014,6,10,12))

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
      calendario.add_excepcion_laborable(DT(2014,1,2),DT(2014,1,1))
      self.fail(_(u'La fecha desde no debería ser mayor que la fecha hasta.'))
    except FechaDesdeMayorFechaHasta:
      pass

    try:
      calendario.add_excepcion_no_laborable(DT(2014,1,2),DT(2014,1,1))
      self.fail(_(u'La fecha desde no debería ser mayor que la fecha hasta.'))
    except FechaDesdeMayorFechaHasta:
      pass

    calendario.add_excepcion_laborable(DT(2014,2,1),DT(2014,2,4))

    try:
      calendario.add_excepcion_laborable(DT(2014,2,1),DT(2014,2,4))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_no_laborable(DT(2014,2,1),DT(2014,2,4))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_laborable(DT(2014,1,30),DT(2014,2,6))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_no_laborable(DT(2014,1,30),DT(2014,2,6))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_laborable(DT(2014,1,30),DT(2014,2,3))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_no_laborable(DT(2014,1,30),DT(2014,2,3))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_laborable(DT(2014,2,3),DT(2014,2,6))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_no_laborable(DT(2014,2,3),DT(2014,2,6))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_laborable(DT(2014,2,2),DT(2014,2,3))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    try:
      calendario.add_excepcion_no_laborable(DT(2014,2,2),DT(2014,2,3))
      self.fail(_(u'No debería permitir solapar excepciones laborables/no laborables.'))
    except SolapamientoExcepcionesLaborales:
      pass

    calendario.add_excepcion_no_laborable(DT(2014,2,6),DT(2014,2,7))

