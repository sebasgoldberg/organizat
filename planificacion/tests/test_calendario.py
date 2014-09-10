# coding=utf-8
from .base import *

class PlanificacionSoloLunesDe8A12TestCase(PlanificadorTestCase):

  fixtures = [ getFixture('planificar_con_maquinas_inactivas.json') ]

  def test_planificacion_solo_lunes_8_a_12(self):

    calendario = CalendarioProduccion.get_instance()
    calendario.add_intervalos_laborables(
      dias_laborables=[DiaSemana.LUNES], hora_desde=T(8), hora_hasta=T(12))

    IntervaloCronograma.objects.all().delete()

    cronograma = Cronograma.objects.get(descripcion='Solo neumáticos de auto')

    cronograma.planificar()

    for intervalo in cronograma.get_intervalos():
      huecos = [ h for h in calendario.get_huecos(
        intervalo.fecha_desde,
        hasta=intervalo.get_fecha_hasta()) ]
      hueco = huecos[0]
      self.assertEqual(intervalo.fecha_desde, hueco.fecha_desde)
      self.assertEqual(intervalo.get_fecha_hasta(), hueco.get_fecha_hasta())


class PlanificacionSoloLunesDe8A12DoblePedidoTestCase(PlanificadorTestCase):

  fixtures = [ getFixture('planificar_con_calendario.json') ]

  def test_planificacion_solo_lunes_8_a_12(self):

    calendario = CalendarioProduccion.get_instance()

    cronograma = Cronograma.objects.get(descripcion='Cronograma con pedido de neumáticos de motos y de autos')

    cronograma.invalidar(forzar=True) 

    cronograma.planificar()

    for intervalo in cronograma.get_intervalos():
      huecos = [ h for h in calendario.get_huecos(
        intervalo.fecha_desde,
        hasta=intervalo.get_fecha_hasta()) ]
      hueco = huecos[0]
      self.assertEqual(intervalo.fecha_desde, hueco.fecha_desde)
      self.assertEqual(intervalo.get_fecha_hasta(), hueco.get_fecha_hasta())

  def test_optimizado(self):
    
    calendario = CalendarioProduccion.get_instance()

    cronograma = Cronograma.objects.get(descripcion='Cronograma con pedido de neumáticos de motos y de autos')

    cronograma.invalidar(forzar=True)

    cronograma.optimizar_planificacion = True
    cronograma.tiempo_minimo_intervalo = D(30)
    cronograma.save()

    cronograma.planificar()

    for intervalo in cronograma.get_intervalos():
      huecos = [ h for h in calendario.get_huecos(
        intervalo.fecha_desde,
        hasta=intervalo.get_fecha_hasta()) ]
      hueco = huecos[0]
      self.assertEqual(intervalo.fecha_desde, hueco.fecha_desde)
      self.assertEqual(intervalo.get_fecha_hasta(), hueco.get_fecha_hasta())


