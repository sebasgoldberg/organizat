# coding=utf-8
from .base import *

class ActivacionCronogramaTestCase(PlanificadorTestCase):

  fixtures = [ getFixture('dos_cronogramas.json') ]

  def setUp(self):

    self.c1 = Cronograma.objects.get(descripcion="Crono pedidos B y C")
    self.c2 = Cronograma.objects.get(descripcion="Otro crono")

    self.c1.fecha_inicio = self.c2.fecha_inicio
    self.c1.save()
    self.c2.save()

  def test_activo_c1_planifico_c2(self):
    self.c1.invalidar(forzar=True)
    self.c2.invalidar(forzar=True)
    self.c1.planificar()
    self.c1.activar()
    self.c2.planificar()
    self.validar_no_existe_solapamiento()

  def test_activo_c2_planifico_c1(self):
    self.c1.invalidar(forzar=True)
    self.c2.invalidar(forzar=True)
    self.c2.planificar()
    self.c2.activar()
    self.c1.planificar()
    self.validar_no_existe_solapamiento()

  def test_activo_todo(self):
    self.c1.invalidar(forzar=True)
    self.c2.invalidar(forzar=True)
    self.c2.planificar()
    self.c2.activar()
    self.c1.planificar()
    self.c1.activar()
    self.validar_no_existe_solapamiento()

  def test_planifico_luego_activo(self):
    self.c1.invalidar(forzar=True)
    self.c2.invalidar(forzar=True)
    self.c2.planificar()
    self.c1.planificar()
    self.c2.activar()

    self.c1 = Cronograma.objects.get(descripcion="Crono pedidos B y C")
    self.assertFalse(self.c1.is_valido())

    self.assertRaises(EstadoCronogramaError, self.c1.activar)
    self.assertTrue(self.c1.is_invalido())

    self.c1.planificar()
    self.c1.activar()

    self.validar_no_existe_solapamiento()

  def validar_no_existe_solapamiento(self):
    """
    Se verifica que no existan solapamientos.
    """
    for maquina in MaquinaPlanificacion.objects.all():
      fecha_hasta_anterior = None
      for intervalo in maquina.intervalocronograma_set.order_by('fecha_desde'):
        if fecha_hasta_anterior is None:
          fecha_hasta_anterior = intervalo.fecha_hasta
        else:
          self.assertLessEqual(fecha_hasta_anterior, intervalo.fecha_desde)

class CantidadTareaRealTestCase(PlanificadorTestCase):

  fixtures = [ getFixture('planificar_con_maquinas_inactivas.json') ]

  def test_validaciones_asignacion_cantidad_tarea_real(self):

    IntervaloCronograma.objects.all().delete()

    cronograma = Cronograma.objects.get(descripcion='Solo neumáticos de auto')

    algun_producto_del_cronograma = None
    for pedido in cronograma.get_pedidos():
      for item in pedido.get_items():
        algun_producto_del_cronograma = item.producto
        break
      break

    tarea_primer_grado = algun_producto_del_cronograma.get_tareas_ordenadas_por_dependencia()[0]

    tarea_dependiente = DependenciaTareaProducto.objects.filter(
      producto=algun_producto_del_cronograma, tarea_anterior=tarea_primer_grado).first().tarea

    cronograma.planificar()

    intervalo_primer_grado = IntervaloCronograma.objects.filter(cronograma=cronograma, 
      tarea=tarea_primer_grado).order_by('fecha_desde').first()

    intervalo_dependiente = IntervaloCronograma.objects.filter(cronograma=cronograma, 
      tarea=tarea_dependiente).order_by('fecha_desde').first()

    intervalo_primer_grado.cantidad_tarea_real = intervalo_primer_grado.cantidad_tarea / 2
    try:
      intervalo_primer_grado.clean()
      self.fail(_(u'La cantidad de tarea real solo puede ser asignada en intervalos pertenecientes a cronogramas activos.'))
    except TareaRealEnCronogramaInactivo:
      pass

    cronograma.activar()

    cronograma.desactivar()

    cronograma.activar()

    intervalo_primer_grado = IntervaloCronograma.objects.filter(cronograma=cronograma, 
      tarea=tarea_primer_grado).order_by('fecha_desde').first()

    intervalo_dependiente = IntervaloCronograma.objects.filter(cronograma=cronograma, 
      tarea=tarea_dependiente).order_by('fecha_desde').first()

    intervalo_primer_grado.cantidad_tarea_real = intervalo_primer_grado.cantidad_tarea + 1
    try:
      intervalo_primer_grado.clean()
      self.fail(_(u'La cantidad de tarea real supera la cantidad de tarea planificada.'))
    except TareaRealSuperaPlanificada:
      pass

    intervalo_primer_grado.cantidad_tarea_real = intervalo_primer_grado.cantidad_tarea / 2
    intervalo_primer_grado.clean()
    intervalo_primer_grado.save()

    try:
      intervalo_dependiente.finalizar(intervalo_primer_grado.cantidad_tarea / 2)
      self.fail(_(u'La cantidad de tarea real en el intervalo %s supera la cantidad de tarea real en el intervalo %s.') % (
        intervalo_dependiente, intervalo_primer_grado))
    except TareaRealNoRespetaDependencias:
      pass

    intervalo_primer_grado.finalizar()

    intervalo_primer_grado.cantidad_tarea_real = intervalo_primer_grado.cantidad_tarea_real - 1
    self.assertRaises(EstadoIntervaloCronogramaError,intervalo_primer_grado.clean)

    self.assertRaises(TareaRealNoRespetaDependencias,
      intervalo_dependiente.finalizar, intervalo_dependiente.cantidad_tarea)

    intervalo_dependiente.finalizar(intervalo_primer_grado.cantidad_tarea_real)

    try:
      cronograma.desactivar()
      self.fail(_(u'No debería poder desactivarse un cronograma que tiene intervalos con cantidad de tarea real.'))
    except EstadoIntervaloCronogramaError:
      pass

class EstadoIntervaloCronogramaTestCase(PlanificadorTestCase):

  fixtures = [ getFixture('planificar_con_maquinas_inactivas.json') ]

  def test_validaciones_finalizar_cancelar_intervalo(self):

    IntervaloCronograma.objects.all().delete()

    cronograma = Cronograma.objects.get(descripcion='Solo neumáticos de auto')

    algun_producto_del_cronograma = None
    for pedido in cronograma.get_pedidos():
      for item in pedido.get_items():
        algun_producto_del_cronograma = item.producto
        break
      break

    tarea_primer_grado = algun_producto_del_cronograma.get_tareas_ordenadas_por_dependencia()[0]

    cronograma.planificar()

    intervalo_primer_grado = IntervaloCronograma.objects.filter(cronograma=cronograma, 
      tarea=tarea_primer_grado).order_by('fecha_desde').first()

    try:
      intervalo_primer_grado.finalizar(intervalo_primer_grado.cantidad_tarea / 2)
      self.fail(_(u'No debería ser posible finalizar un intervalo perteneciente a un cronograma inactivo.'))
    except IntervaloFinalizadoEnCronogramaInactivo:
      pass

    self.assertRaises(EstadoIntervaloCronogramaError,intervalo_primer_grado.cancelar)

    cronograma.activar()

    cronograma.desactivar()

    cronograma.activar()

    intervalo_primer_grado = IntervaloCronograma.objects.filter(cronograma=cronograma, 
      tarea=tarea_primer_grado).order_by('fecha_desde').first()

    intervalo_primer_grado.finalizar(intervalo_primer_grado.cantidad_tarea / 2)

    intervalo_primer_grado = IntervaloCronograma.objects.filter(cronograma=cronograma, 
      tarea=tarea_primer_grado).order_by('fecha_desde').first()

    self.assertTrue(intervalo_primer_grado.is_finalizado())
    self.assertEqual(intervalo_primer_grado.cantidad_tarea_real, intervalo_primer_grado.cantidad_tarea / 2)

    self.assertRaises(EstadoIntervaloCronogramaError,intervalo_primer_grado.cancelar)

    intervalo_primer_grado = IntervaloCronograma.objects.filter(cronograma=cronograma, 
      tarea=tarea_primer_grado).order_by('fecha_desde').first()


class EstadoCronogramaIntervalosTestCase(PlanificadorTestCase):

  fixtures = [ getFixture('planificar_con_calendario.json') ]

  def setUp(self):
    
    self.crono_solo_neumaticos = Cronograma.objects.get(descripcion='Solo neumáticos de auto')
    self.crono_todo = Cronograma.objects.get(descripcion='Cronograma con pedido de neumáticos de motos y de autos')
    
    self.crono_solo_neumaticos.fecha_inicio = self.crono_todo.fecha_inicio
    self.crono_solo_neumaticos.tiempo_minimo_intervalo = 60
    self.crono_todo.tiempo_minimo_intervalo = 60
    self.crono_solo_neumaticos.save()
    self.crono_todo.save()

    Calendario.objects.all().delete()

    calendario = Calendario()
    calendario.clean()
    calendario.save()

    # se define calendario lu a vi de 8 a 12
    calendario.add_intervalos_laborables(
      dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES,
        DiaSemana.MIERCOLES,DiaSemana.JUEVES,DiaSemana.VIERNES],
      hora_desde=T(8), hora_hasta=T(12))
 
    # se redefine calendario lu a vi de 8 a 12 y de 13 a 17
    calendario.add_intervalos_laborables(
      dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES,
        DiaSemana.MIERCOLES,DiaSemana.JUEVES,DiaSemana.VIERNES],
      hora_desde=T(13),hora_hasta=T(17))

  def invalidar_cronogramas(self):
    
    for c in Cronograma.objects.all():
      c.invalidar(forzar=True)

    self.crono_solo_neumaticos = Cronograma.objects.get(descripcion='Solo neumáticos de auto')
    self.crono_todo = Cronograma.objects.get(descripcion='Cronograma con pedido de neumáticos de motos y de autos')

  def test_cantidad_planificada_respeta_cantidad_ya_activa(self):

    self.invalidar_cronogramas()

    self.crono_solo_neumaticos.planificar()
    self.crono_solo_neumaticos.activar()

    self.crono_todo.planificar()
    self.crono_todo.activar()

    for pedido in PedidoPlanificable.objects.all():
      for item in pedido.get_items():
        for tarea in item.producto.get_tareas():
          cantidad_planificada = item.get_cantidad_planificada(tarea)
          self.assertEqual(cantidad_planificada, item.cantidad)
          self.assertEqual(item.get_cantidad_realizada(tarea), 0)
          self.assertEqual(item.get_cantidad_no_planificada(tarea), 0)

  def test_estado_cronograma(self):

    self.invalidar_cronogramas()

    # Estado: Inválido

    self.assertTrue(self.crono_solo_neumaticos.is_invalido())
    self.assertEqual(
      self.crono_solo_neumaticos.intervalocronograma_set.count(), 0)

    self.assertRaises(EstadoCronogramaError,
      self.crono_solo_neumaticos.invalidar)

    self.assertRaises(EstadoCronogramaError,
      self.crono_solo_neumaticos.activar)

    self.assertRaises(EstadoCronogramaError,
      self.crono_solo_neumaticos.desactivar)

    self.crono_solo_neumaticos.planificar()

    # Estado: Válido

    self.assertTrue(self.crono_solo_neumaticos.is_valido())
    self.assertNotEqual(
      self.crono_solo_neumaticos.intervalocronograma_set.count(), 0)
    for i in self.crono_solo_neumaticos.intervalocronograma_set.all():
      self.assertTrue(i.is_planificado())

    self.assertRaises(EstadoCronogramaError,
      self.crono_solo_neumaticos.desactivar)

    self.assertRaises(EstadoCronogramaError,
      self.crono_solo_neumaticos.planificar)

    self.crono_solo_neumaticos.activar()

    # Estado: Activo

    self.assertTrue(self.crono_solo_neumaticos.is_activo())
    self.assertNotEqual(
      self.crono_solo_neumaticos.intervalocronograma_set.count(), 0)
    for i in self.crono_solo_neumaticos.intervalocronograma_set.all():
      self.assertTrue(i.is_activo())

    self.assertRaises(EstadoCronogramaError,
      self.crono_solo_neumaticos.planificar)

    self.assertRaises(EstadoCronogramaError,
      self.crono_solo_neumaticos.activar)

    self.assertRaises(EstadoCronogramaError,
      self.crono_solo_neumaticos.invalidar)

    self.crono_solo_neumaticos.desactivar()

    # Estado: Valido

    self.assertTrue(self.crono_solo_neumaticos.is_valido())
    self.assertNotEqual(
      self.crono_solo_neumaticos.intervalocronograma_set.count(), 0)
    for i in self.crono_solo_neumaticos.intervalocronograma_set.all():
      self.assertTrue(i.is_planificado())

    self.crono_solo_neumaticos.invalidar()

    # Estado: Valido

    self.assertTrue(self.crono_solo_neumaticos.is_invalido())
    self.assertEqual(
      self.crono_solo_neumaticos.intervalocronograma_set.count(), 0)

  def test_finalizacion_parcial_replanificacion(self):
    
    self.invalidar_cronogramas()

    self.assertEqual(0, IntervaloCronograma.objects.count())

    self.crono_solo_neumaticos.planificar()
    self.crono_solo_neumaticos.activar()

    i = 1  
    for intervalo in self.crono_solo_neumaticos.get_intervalos_ordenados_por_dependencia():
      i += 1
      intervalo.finalizar(intervalo.cantidad_tarea / i)

    self.assertEqual(0, IntervaloCronograma.objects.exclude(
      estado=ESTADO_INTERVALO_FINALIZADO).count())

    pedido_solo_neuma_auto = self.crono_solo_neumaticos.get_pedidos()[0]

    for item in pedido_solo_neuma_auto.get_items():
      for tarea in item.producto.get_tareas():
        cantidad_planificada = item.get_cantidad_planificada(tarea)
        self.assertEqual(0, cantidad_planificada)
        self.assertLess(0, item.get_cantidad_realizada(tarea))
        self.assertLess(0, item.get_cantidad_no_planificada(tarea))

    self.crono_todo.planificar()
    self.crono_todo.activar()

    for item in pedido_solo_neuma_auto.get_items():
      for tarea in item.producto.get_tareas():
        cantidad_planificada = item.get_cantidad_planificada(tarea)
        self.assertLess(0, cantidad_planificada)
        self.assertLess(0, item.get_cantidad_realizada(tarea))
        self.assertEqual(0, item.get_cantidad_no_planificada(tarea))

    self.crono_todo.finalizar()

    for item in pedido_solo_neuma_auto.get_items():
      for tarea in item.producto.get_tareas():
        cantidad_planificada = item.get_cantidad_planificada(tarea)
        self.assertEqual(0, cantidad_planificada)
        self.assertEqual(item.cantidad, item.get_cantidad_realizada(tarea))
        self.assertEqual(0, item.get_cantidad_no_planificada(tarea))

  def test_cancelacion_parcial_replanificacion(self):
    
    self.invalidar_cronogramas()

    self.assertEqual(0, IntervaloCronograma.objects.count())

    self.crono_solo_neumaticos.planificar()
    
    for intervalo in self.crono_solo_neumaticos.get_intervalos_ordenados_por_dependencia():
      # No se debería poder cancelar un intervalo que no esté activo
      self.assertRaises(EstadoIntervaloCronogramaError,intervalo.cancelar)
      break

    self.crono_solo_neumaticos.activar()

    intervalos = []
    for intervalo in self.crono_solo_neumaticos.get_intervalos_ordenados_por_dependencia():
      intervalos.append(intervalo)

    # Se obtiene un intervalo con grado intermedio
    indice_intermedio = len(intervalos) / 2
    intervalo_cancelado = intervalos[indice_intermedio]

    # Se asigna 10 a la cantidad de tarea real.
    intervalo_cancelado.cantidad_tarea_real = 10
    intervalo_cancelado.clean()
    intervalo_cancelado.save()

    intervalo_cancelado.cancelar()

    # Luego de cancelar el intervalo se verifica que esté cancelado
    # y que la cantidad de tarea real sea nula
    self.assertTrue(intervalo_cancelado.is_cancelado())
    self.assertEqual(intervalo_cancelado.cantidad_tarea_real, 0)

    intervalo_cancelado.cantidad_tarea_real = 10
    # No se puede modificar un intervalo cancelado
    self.assertRaises(EstadoIntervaloCronogramaError, intervalo_cancelado.clean)

    # Se verifica que los intervalos subsiguientes hayan sido cancelados.
    for intervalo_dependiente in intervalo_cancelado.get_intervalos_dependientes():
      self.assertTrue(intervalo_dependiente.is_cancelado())

    self.crono_todo.planificar()

    # Se verifica que coincidan los intervalos planificados del pedido de
    # neumáticos de autos con los intervalos cancelados.
    pedido_neumaticos = self.crono_solo_neumaticos.get_pedidos()[0]
    cantidadTarea={}

    for intervaloCancelado in IntervaloCronograma.objects.filter(
        cronograma=self.crono_solo_neumaticos,
        estado=ESTADO_INTERVALO_CANCELADO): 
        cantidadTarea.setdefault(intervaloCancelado.tarea.id,0)
        cantidadTarea[intervaloCancelado.tarea.id]+=intervaloCancelado.cantidad_tarea;

    for intervaloPlanificado in IntervaloCronograma.objects.filter(
        cronograma=self.crono_todo,
        item__in=[i for i in pedido_neumaticos.get_items()]):
        cantidadTarea[intervaloPlanificado.tarea.id]-=intervaloPlanificado.cantidad_tarea;

    for cantidad in cantidadTarea.itervalues():
        self.assertEqual(cantidad, 0)
        

class DeberiaDejarCancelarIntervalo60(PlanificadorTestCase):
  
  fixtures = [ getFixture('deberia_dejar_cancelar_intervalo_60.json') ]
  
  def _fixture_setup(self):
    post_save.disconnect(add_maquinas_posibles_to_cronograma, 
      sender=PedidoCronograma)
    result = super(DeberiaDejarCancelarIntervalo60, self)._fixture_setup()
    return result

  def _fixture_teardown(self):
    post_save.connect(add_maquinas_posibles_to_cronograma, 
      sender=PedidoCronograma)
    result = super(DeberiaDejarCancelarIntervalo60, self)._fixture_teardown()
    return result

  def test_cancelar_intervalo_60(self):

    intervalo = IntervaloCronograma.objects.get(pk=60)

    intervalo.cancelar()


