# coding=utf-8
from django.test import TestCase
from produccion.models import * 
from planificacion.models import * 
from calendario.models import DiaSemana
import datetime
import pytz
from django.db.transaction import rollback
from django.utils.translation import ugettext as _
from datetime import time as T
from datetime import datetime as DT
from decimal import Decimal as D
from calendario.models import *

utc=pytz.UTC

class PlanificadorTestCase(TestCase):

  def verificar_cantidad_planificada(self, cronograma):

    # Se verifica que se haya planificado la cantidad 
    # que corresponde de cada tarea.
    for pedido in cronograma.get_pedidos():
      for item in pedido.get_items():
        for tarea in item.producto.get_tareas():
          cantidad_tarea = cronograma.intervalocronograma_set.filter(
            tarea=tarea,pedido=pedido,producto=item.producto).aggregate(
            models.Sum('cantidad_tarea'))['cantidad_tarea__sum']
          self.assertEqual(item.cantidad, cantidad_tarea, 
            'Intervalos involucrados: %s' % cronograma.intervalocronograma_set.filter(
              tarea=tarea,pedido=pedido,producto=item.producto))

  def test_fecha_hasta(self):
    for intervalo in IntervaloCronograma.objects.all():
      if not intervalo.fecha_hasta:
        intervalo.clean()
        intervalo.save()
      self.assertLessEqual(abs((intervalo.fecha_hasta - intervalo.get_fecha_hasta()).total_seconds()),1)


class TiempoRealizacionTareaTestCase(TestCase):

  def setUp(self):

    M1=MaquinaPlanificacion.objects.create(descripcion='M1')
    M2=MaquinaPlanificacion.objects.create(descripcion='M2')
    M3=MaquinaPlanificacion.objects.create(descripcion='M3')

    T1=Tarea.objects.create(descripcion='T1', tiempo=5)
    T2=Tarea.objects.create(descripcion='T2', tiempo=10)
    T3=Tarea.objects.create(descripcion='T3', tiempo=3.5)

    """
          T1    T2    T3
    M1    X
    M2    X     X
    M3          X     X
    """
    TareaMaquina.objects.create(tarea=T1,maquina=M1)
    TareaMaquina.objects.create(tarea=T1,maquina=M2)
    TareaMaquina.objects.create(tarea=T2,maquina=M2)
    TareaMaquina.objects.create(tarea=T2,maquina=M3)
    TareaMaquina.objects.create(tarea=T3,maquina=M3)

    P1=Producto.objects.create(descripcion='P1')
    P2=Producto.objects.create(descripcion='P2')
    P3=Producto.objects.create(descripcion='P3')

    """
          T1    T2    T3
    P1    X     X
    P2    X           X
    P3    X     X     X
    """
    TareaProducto.objects.create(tarea=T1,producto=P1)
    TareaProducto.objects.create(tarea=T2,producto=P1)
    TareaProducto.objects.create(tarea=T1,producto=P2)
    TareaProducto.objects.create(tarea=T3,producto=P2)
    TareaProducto.objects.create(tarea=T1,producto=P3)
    TareaProducto.objects.create(tarea=T2,producto=P3)
    TareaProducto.objects.create(tarea=T3,producto=P3)

    D1=PedidoPlanificable.objects.create(descripcion='D1')
    D2=PedidoPlanificable.objects.create(descripcion='D2')
    D3=PedidoPlanificable.objects.create(descripcion='D3')

    """
          D1    D2    D3
    P1    100         300
    P2    200   150
    P3          150
    """
    D1.add_item(P1,100)
    D1.add_item(P2,200)

    D2.add_item(P3,150)
    D2.add_item(P2,150)

    D3.add_item(P1,300)

    cronograma = Cronograma(descripcion='CRON1', estrategia=2)
    cronograma.clean()
    cronograma.save()

    cronograma.add_maquina(M1)
    cronograma.add_maquina(M2)
    cronograma.add_maquina(M3)

    cronograma.add_pedido(D1)
    cronograma.add_pedido(D2)
    cronograma.add_pedido(D3)

  def test_planificar(self):
    
    cronograma = Cronograma.objects.get(descripcion='CRON1')

    cronograma.planificar()

class IntervaloCronogramaTestCase(TestCase):

  def setUp(self):

    M1=MaquinaPlanificacion.objects.create(descripcion='M1')
    M2=MaquinaPlanificacion.objects.create(descripcion='M2')
    M3=MaquinaPlanificacion.objects.create(descripcion='M3')

    T1=Tarea.objects.create(descripcion='T1', tiempo=5)
    T2=Tarea.objects.create(descripcion='T2', tiempo=10)
    T3=Tarea.objects.create(descripcion='T3', tiempo=3.5)

    """
          T1    T2    T3
    M1    X
    M2    X     X
    M3          X     X
    """
    TareaMaquina.objects.create(tarea=T1,maquina=M1)
    TareaMaquina.objects.create(tarea=T1,maquina=M2)
    TareaMaquina.objects.create(tarea=T2,maquina=M2)
    TareaMaquina.objects.create(tarea=T2,maquina=M3)
    TareaMaquina.objects.create(tarea=T3,maquina=M3)

    P1=Producto.objects.create(descripcion='P1')
    P2=Producto.objects.create(descripcion='P2')
    P3=Producto.objects.create(descripcion='P3')

    """
          T1    T2    T3
    P1    X     X
    P2    X           X
    P3    X     X     X
    """
    TareaProducto.objects.create(tarea=T1,producto=P1)
    TareaProducto.objects.create(tarea=T2,producto=P1)
    TareaProducto.objects.create(tarea=T1,producto=P2)
    TareaProducto.objects.create(tarea=T3,producto=P2)
    TareaProducto.objects.create(tarea=T1,producto=P3)
    TareaProducto.objects.create(tarea=T2,producto=P3)
    TareaProducto.objects.create(tarea=T3,producto=P3)

    D1=PedidoPlanificable.objects.create(descripcion='D1')
    D2=PedidoPlanificable.objects.create(descripcion='D2')
    D3=PedidoPlanificable.objects.create(descripcion='D3')

    """
          D1    D2    D3
    P1    100         300
    P2    200   150
    P3          150
    """
    D1.add_item(P1,100)
    D1.add_item(P2,200)

    D2.add_item(P3,150)
    D2.add_item(P2,150)

    D3.add_item(P1,300)

    cronograma = Cronograma(descripcion='CRON1', estrategia=2, 
      fecha_inicio=datetime.datetime(2014,1,1,0,0,0),tiempo_minimo_intervalo=0)

    cronograma.clean()
    cronograma.save()

    cronograma.add_maquina(M1)
    cronograma.add_maquina(M2)
    cronograma.add_maquina(M3)

    cronograma.add_pedido(D1)
    cronograma.add_pedido(D2)
    cronograma.add_pedido(D3)

  def test_calcular_fecha_desde(self):
    
    cronograma = Cronograma.objects.get(descripcion='CRON1')
    M1 = MaquinaPlanificacion.objects.get(descripcion='M1')
    T1 = Tarea.objects.get(descripcion='T1')
    P1 = Producto.objects.get(descripcion='P1')
    D1 = PedidoPlanificable.objects.get(descripcion='D1')
    
    intervalo=IntervaloCronograma(cronograma=cronograma,maquina=M1,
      tarea=T1,producto=P1,pedido=D1,cantidad_tarea=100/5,
      tiempo_intervalo=100)
    intervalo.clean()
    intervalo.save()

    intervalo=IntervaloCronograma(cronograma=cronograma,maquina=M1,
      tarea=T1,producto=P1,pedido=D1,cantidad_tarea=100/5,
      tiempo_intervalo=100)
    intervalo.clean()

    self.assertEqual(intervalo.fecha_desde,utc.localize(datetime.datetime(2014,1,1,1,40,0)))

    intervalo.save()

    fecha_hasta = intervalo.get_fecha_hasta()
    intervalo=IntervaloCronograma(cronograma=cronograma,maquina=M1,
      tarea=T1,producto=P1,pedido=D1,cantidad_tarea=100/5,
      tiempo_intervalo=100, fecha_desde=fecha_hasta)

    self.assertEqual(intervalo.fecha_desde,fecha_hasta)


class TareaDependienteTestCase(TestCase):

  def setUp(self):

    M1=MaquinaPlanificacion.objects.create(descripcion='M1')
    M2=MaquinaPlanificacion.objects.create(descripcion='M2')

    T1=Tarea.objects.create(descripcion='T1', tiempo=5)
    T2=Tarea.objects.create(descripcion='T2', tiempo=10)

    TareaMaquina.objects.create(tarea=T1,maquina=M1)
    TareaMaquina.objects.create(tarea=T2,maquina=M2)

    P1=Producto.objects.create(descripcion='P1')

    TareaProducto.objects.create(tarea=T1,producto=P1)
    TareaProducto.objects.create(tarea=T2,producto=P1)

    D1=PedidoPlanificable.objects.create(descripcion='D1')

    D1.add_item(P1,100)

    cronograma = Cronograma(descripcion='CRON1', estrategia=2, 
      fecha_inicio=datetime.datetime(2014,1,1,0,0,0), tiempo_minimo_intervalo=0)

    cronograma.clean()
    cronograma.save()

    cronograma.add_maquina(M1)
    cronograma.add_maquina(M2)

    cronograma.add_pedido(D1)

    P1.add_dependencia_tareas(tarea_anterior=T1,tarea=T2)

  def test_calcular_fecha_desde(self):
    
    cronograma = Cronograma.objects.get(descripcion='CRON1')
    M1 = MaquinaPlanificacion.objects.get(descripcion='M1')
    M2 = MaquinaPlanificacion.objects.get(descripcion='M2')
    T1 = Tarea.objects.get(descripcion='T1')
    T2 = Tarea.objects.get(descripcion='T2')
    P1 = Producto.objects.get(descripcion='P1')
    D1 = PedidoPlanificable.objects.get(descripcion='D1')

    # Se verifica la obtención de tareas ordenadas por grado de dependencia
    tareas_ordenadas_por_grado_dependencia=P1.get_tareas_ordenadas_por_dependencia()
    self.assertEqual(tareas_ordenadas_por_grado_dependencia[0].id,T1.id)
    self.assertEqual(tareas_ordenadas_por_grado_dependencia[1].id,T2.id)
    
    # Se agrega una tarea T1 entre [0;25] como resultado da una cantidad de 5
    I1=IntervaloCronograma(cronograma=cronograma,maquina=M1,
      tarea=T1,producto=P1,pedido=D1,cantidad_tarea=25/5,
      tiempo_intervalo=25, fecha_desde=cronograma.fecha_inicio)
    I1.clean()
    I1.save()


    # Se planifica I2 en la máquina M2 en la fecha de finalización de I1
    I2=IntervaloCronograma(cronograma=cronograma,maquina=M2,
      tarea=T2,producto=P1,pedido=D1,cantidad_tarea=100/10,
      tiempo_intervalo=100, fecha_desde=I1.get_fecha_hasta())

    # Se verifica que cuando se asigna la fecha desde, el cálculo no la modifica.
    self.assertEqual(I2.get_fecha_desde(),I1.get_fecha_hasta())

    # Se verifica que la obtención de los intervalos sea correcta:
    intervalos = [ i for i in GerenciadorDependencias.crear_desde_instante(
      I2).get_intervalos([T1,T2],instante_agregado=I2) ]
    self.assertEqual(len(intervalos),2)

    try:
      # como I1:M1:T1:5:[0;25] y I2:M2:T2:10:[25;125] y T1 -> T2 => 
      # => En 75 ya no se puede seguir produciendo T2
      # Por lo tanto debe ocurrir un error.
      I2.clean()
      I2.save()
      self.fail("No aplico la validacion de cantidad de tarea anterior necesaria para tarea agregada.")
    except ValidationError:
      pass

    # Modificamos la fecha de inicio de I2 para que coincida con I1:
    I2.fecha_desde = I1.get_fecha_desde()

    try:
      # como I1:M1:T1:5:[0;25] y I2:M2:T2:10:[0;100] y T1 -> T2 => 
      # => En 50 ya no se puede seguir produciendo T2
      # Por lo tanto debe ocurrir un error.
      I2.clean()
      I2.save()
      self.fail("No aplico la validacion de cantidad de tarea anterior necesaria para tarea agregada.")
    except ValidationError:
      pass

    # Agregamos el intervalo I3:M1:T1:5:[25;50]
    I3=IntervaloCronograma(cronograma=cronograma,maquina=M1,
      tarea=T1,producto=P1,pedido=D1,cantidad_tarea=25/5,
      tiempo_intervalo=25, fecha_desde=I1.get_fecha_hasta())
    I3.clean()
    I3.save()
    
    # Verificamos que la fecha de inicio de I3 coincida con la de I1 finalización de I1:
    self.assertEqual(I3.get_fecha_desde(),I1.get_fecha_hasta())

    # como I1:M1:T1:5:[0;25] y I3:M1:T1:5:[25;50] y I2:M2:T2:10:[0;100] y T1 -> T2 => 
    # Vemos que no hay problemas de dependencia
    I2.clean()
    I2.save()

    self.assertEqual(utc.localize(datetime.datetime(2014,1,1,0,0,0)),I1.get_fecha_desde())
    self.assertEqual(utc.localize(datetime.datetime(2014,1,1,0,25,0)),I1.get_fecha_hasta())
    self.assertEqual(utc.localize(datetime.datetime(2014,1,1,0,0,0)),I2.get_fecha_desde())
    self.assertEqual(utc.localize(datetime.datetime(2014,1,1,1,40,0)),I2.get_fecha_hasta())

    # Se verifica que la obtención de los intervalos sea correcta:
    gd = GerenciadorDependencias.crear_desde_instante(I3)
    intervalos = [i for i in gd.get_intervalos([T1,T2],instante_borrado=I3)]
    self.assertEqual(len(intervalos),2)

    # Se verifica que no se hata recuperado el intervalo I3
    for intervalo in intervalos:
      self.assertNotEqual(intervalo.id,I3.id)

    # Se verifica que se obtengan la particion que corresponde: {0, 25, 100}
    particion_temporal = gd.get_particion_ordenada_temporal(intervalos)
    self.assertEqual(len(particion_temporal),3)
    self.assertEqual(utc.localize(datetime.datetime(2014,1,1,0,0,0)),particion_temporal[0])
    self.assertEqual(utc.localize(datetime.datetime(2014,1,1,0,25,0)),particion_temporal[1])
    self.assertEqual(utc.localize(datetime.datetime(2014,1,1,1,40,0)),particion_temporal[2])

    cantidad_tarea_posterior = gd.get_cantidad_tarea_hasta(intervalos, T2, particion_temporal[0])
    self.assertEqual(cantidad_tarea_posterior,0)
    cantidad_tarea_anterior = gd.get_cantidad_tarea_hasta(intervalos, T1, particion_temporal[0])
    self.assertEqual(cantidad_tarea_anterior,0)

    # Acá es donde la cantidad de la tarea posterior supera a la cantidad de la tarea anterior
    cantidad_tarea_posterior = gd.get_cantidad_tarea_hasta(intervalos, T2, particion_temporal[1])
    self.assertEqual(cantidad_tarea_posterior,2.5)
    cantidad_tarea_anterior = gd.get_cantidad_tarea_hasta(intervalos, T1, particion_temporal[1])
    self.assertEqual(cantidad_tarea_anterior,5)

    cantidad_tarea_posterior = gd.get_cantidad_tarea_hasta(intervalos, T2, particion_temporal[2])
    self.assertEqual(cantidad_tarea_posterior,10)
    cantidad_tarea_anterior = gd.get_cantidad_tarea_hasta(intervalos, T1, particion_temporal[2])
    self.assertEqual(cantidad_tarea_anterior,5)

    # Si queremos quitar I3 deberíamos obtener un error, ya que se dejaría de cumplir
    # la dependencia T1 -> T2
    try:
      gerenciador_dependencias = GerenciadorDependencias.crear_desde_instante(I3)
      gerenciador_dependencias.validar_dependencias(T1,T2,instante_borrado=I3)
      self.fail("Debería ser inválido quitar el instante I3.")
    except ValidationError:
      pass

    # Se verifica que efectivamente T2 está dentro de las tareas posteriores a T1
    self.assertIn(T2.id,[t.id for t in T1.get_posteriores(P1)])

    # Si queremos quitar I3 deberíamos obtener un error, ya que se dejaría de cumplir
    # la dependencia T1 -> T2
    try:
      gerenciador_dependencias = GerenciadorDependencias.crear_desde_instante(I3)
      gerenciador_dependencias.verificar_eliminar_instante(I3)
      self.fail("Debería ser inválido quitar el instante I3.")
    except ValidationError:
      pass

    # Si queremos quitar I3 deberíamos obtener un error, ya que se dejaría de cumplir
    # la dependencia T1 -> T2
    try:
      I3.delete()
      self.fail("No deberia dejar borrar un intervalo que hace que no se cumpla una dependencia.")
    except ValidationError:
      pass

    I3.fecha_desde = I2.get_fecha_hasta()
    try:
      I3.clean()
      I3.save()
      self.fail("Debería ser inválido mover el instante I3 después del instante I2.")
    except ValidationError:
      pass

    I4=IntervaloCronograma(cronograma=cronograma,maquina=M2,
      tarea=T2,producto=P1,pedido=D1,cantidad_tarea=100/10,
      tiempo_intervalo=100, fecha_desde=I2.get_fecha_hasta())

    try:
      # como I1:M1:T1:5:[0;25] y I2:M2:T2:10:[0;100] y T1 -> T2 => 
      # => En 50 ya no se puede seguir produciendo T2
      # Por lo tanto debe ocurrir un error.
      I4.clean()
      I4.save()
      self.fail("No aplico la validacion de cantidad de tarea anterior necesaria para tarea agregada.")
    except ValidationError:
      self.assertEqual(I4.get_fecha_desde(),I2.get_fecha_hasta())

class PlanificadorLinealContinuoTestCase(PlanificadorTestCase):
  
  def setUp(self):

    M1=MaquinaPlanificacion.objects.create(descripcion='M1')
    M2=MaquinaPlanificacion.objects.create(descripcion='M2')

    T1=Tarea.objects.create(descripcion='T1', tiempo=5)
    T2=Tarea.objects.create(descripcion='T2', tiempo=10)

    TareaMaquina.objects.create(tarea=T1,maquina=M1)
    TareaMaquina.objects.create(tarea=T2,maquina=M2)

    P1=Producto.objects.create(descripcion='P1')

    TareaProducto.objects.create(tarea=T1,producto=P1)
    TareaProducto.objects.create(tarea=T2,producto=P1)

    D1=PedidoPlanificable.objects.create(descripcion='D1')

    D1.add_item(P1,100)

    cronograma = Cronograma(descripcion='CRON1', estrategia=2, 
      fecha_inicio=datetime.datetime(2014,1,1,0,0,0),)

    cronograma.clean()
    cronograma.save()

    cronograma.add_maquina(M1)
    cronograma.add_maquina(M2)

    cronograma.add_pedido(D1)

    P1.add_dependencia_tareas(tarea_anterior=T2,tarea=T1)

  def test_completar_cronograma(self):
 
    cronograma = Cronograma.objects.get(descripcion='CRON1')
    D1 = PedidoPlanificable.objects.get(descripcion='D1')
    P1 = Producto.objects.get(descripcion='P1')
    T1 = Tarea.objects.get(descripcion='T1')
    T2 = Tarea.objects.get(descripcion='T2')

    #T2.get_secuencias_dependencias()

    # Se verifica que T2 sea la tarea con primer grado de dependencia.
    tareas = P1.get_tareas_primer_grado_dependencia()
    self.assertEqual(len(tareas),1)
    self.assertEqual(T2.id,tareas[0].id)

    # Se verifica el correcto funcionamiento de la obtención de tareas
    # ordenadas por dependencia.
    tareas=P1.get_tareas_ordenadas_por_dependencia()
    self.assertEqual(len(tareas),2)
    self.assertEqual(T2.id,tareas[0].id)
    self.assertEqual(T1.id,tareas[1].id)

    # Se verifica que no existan tareas anteriores para la tarea T2,
    # en el producto P1
    self.assertEqual(len(T2.get_anteriores(P1)),0)

    cronograma.planificar()

    self.verificar_cantidad_planificada(cronograma)

class HuecoInexplicableTestCase(PlanificadorTestCase):
  
  fixtures = [ 'planificacion/fixtures/tests/hueco_inexplicable.json' ]

  def test_no_existe_hueco_inexplicable(self):

    # Se recupera el primero, porque hay un solo cronograma definido.
    cronograma = Cronograma.objects.get(pk=1)

    cronograma.planificar()

    self.verificar_cantidad_planificada(cronograma)

    M3 = MaquinaPlanificacion.objects.get(descripcion='M3')

    huecos = []
    for hueco in cronograma.get_huecos(M3):
      huecos.append(hueco)
      break

    if len(huecos) == 0:
      return

    hueco = huecos[0]

    self.assertLess(hueco.fecha_desde,hueco.get_fecha_hasta())

    # Se obtiene el intervalo posterior al hueco.
    intervalo = IntervaloCronograma.objects.get(maquina=M3, fecha_desde=hueco.get_fecha_hasta()) 

    intervalo.fecha_desde = hueco.fecha_desde
    intervalo.clean()
    intervalo.save()

class TiempoMinimoDeBloqueTestCase(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/hueco_inexplicable.json' ]

  def setUp(self):

    # Se recupera el primero, porque hay un solo cronograma definido.
    cronograma = Cronograma.objects.get(pk=1)

    cronograma.planificar()

  def test_tiempo_minimo_bloque(self):

    cronograma = Cronograma.objects.get(pk=1)

    for intervalo in cronograma.intervalocronograma_set.all():
      self.assertLessEqual(intervalo.cronograma.tiempo_minimo_intervalo,intervalo.tiempo_intervalo,
        u'El intervalo %s tiene un tiempo %s menor al tiempo mínimo %s.' % (
          intervalo, intervalo.tiempo_intervalo, intervalo.cronograma.tiempo_minimo_intervalo))

class TiempoMenorAlTiempoMinimoTestCase(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/hueco_inexplicable.json' ]

  def setUp(self):

    pedido=PedidoPlanificable(descripcion='D4')
    pedido.clean()
    pedido.save()

    P1 = Producto.objects.first()

    pedido.add_item(P1,1)

    cronograma = Cronograma.objects.get(pk=1)
    cronograma.add_pedido(pedido)
    cronograma.tiempo_minimo_intervalo = 120
    cronograma.clean()
    cronograma.save()

  def test_tiempo_menor_al_tiempo_minimo(self):

    cronograma = Cronograma.objects.get(pk=1)

    tiempo_minimo_intervalo = cronograma.tiempo_minimo_intervalo

    cronograma.planificar()

    # Tomamos cualquier intervalo del pedido D4
    intervalo = IntervaloCronograma.objects.filter(pedido__descripcion='D4').first()

    # Verificamos que el intervalo tiene una duración menor a la del tiempo mínimo
    self.assertLess(intervalo.tiempo_intervalo,tiempo_minimo_intervalo)

class PlanificarSinHuecosEvitables(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/hueco_inexplicable.json' ]

  def setUp(self):

    cronograma = Cronograma.objects.get(pk=1)

    cronograma.tiempo_minimo_intervalo = 0
    cronograma.clean()
    cronograma.save()
    cronograma.planificar()

  def test_planificar_sin_huecos_evitables(self):

    cronograma = Cronograma.objects.get(pk=1)

    cronograma.optimizar_planificacion = True
    cronograma.save()

    cronograma.invalidar(forzar=True)

    cronograma.planificar()

    for intervalo in cronograma.get_intervalos():
      try:
        fecha_inicial = intervalo.fecha_desde
        intervalo.mover(-1)
        intervalo.clean()
        intervalo.save()
        fecha_final = intervalo.fecha_desde
        self.fail(u'Intervalo movido de %s a %s. No se debería poder adelantar una tarea. Debería ser planificada correctamente.' % (
          fecha_inicial, fecha_final))
      except ValidationError:
        pass

class MasDeUnaDependenciaError(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/mas_de_una_dependencia.json' ]

  def setUp(self):

    cronograma = Cronograma.objects.get(pk=1)

    cronograma.clean()
    cronograma.save()
    cronograma.planificar()

  def test_cantidad_planificada(self):
    
    cronograma = Cronograma.objects.get(pk=1)

    self.verificar_cantidad_planificada(cronograma)


class MasDeUnaDependencia120ErrorOperacion(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/mas_de_una_dependencia.json' ]

  def setUp(self):

    cronograma = Cronograma.objects.get(pk=1)

    cronograma.tiempo_minimo_intervalo = 120
    cronograma.clean()
    cronograma.save()
    cronograma.planificar()

  def test_cantidad_planificada(self):
    
    cronograma = Cronograma.objects.get(pk=1)

    self.verificar_cantidad_planificada(cronograma)

class DosCronogramasTestCase(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/dos_cronogramas.json' ]

  def setUp(self):

    cronograma = Cronograma.objects.get(descripcion='Otro crono')

    cronograma.clean()
    cronograma.save()
    cronograma.planificar()

  def test_cantidad_planificada(self):
    
    cronograma = Cronograma.objects.get(descripcion='Otro crono')

    self.verificar_cantidad_planificada(cronograma)

class PlanificarSinTodasLasMaquinas(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/planificar_sin_todas_las_maquinas.json' ]

  def test_planificar_sin_todas_las_maquinas(self):

    cronograma = Cronograma.objects.get(descripcion='Solo neumáticos de auto')

    cronograma.planificar()

    self.verificar_cantidad_planificada(cronograma)


class PlanificarConMaquinasInactivas(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/planificar_con_maquinas_inactivas.json' ]

  def test_planificar_con_maquinas_inactivas(self):

    self.assertEqual(0, TiempoRealizacionTarea.objects.filter(
      activa=False).count())
    
    trt=TiempoRealizacionTarea.objects.get(
      maquina__descripcion='6 - Moldeadora de Neumáticos (MN1)',
      producto__descripcion='Neumático de Auto',
      tarea__descripcion='6 - Moldeado de Neumáticos')
    trt.activa=False
    trt.clean()
    trt.save()

    self.assertLess(0, TiempoRealizacionTarea.objects.filter(
      activa=False).count())

    cronograma = Cronograma.objects.get(descripcion='Solo neumáticos de auto')

    maquinas = trt.tarea.get_maquinas_producto(trt.producto)
    self.assertFalse(trt.maquina in maquinas, '%s not in %s' % (trt.maquina, maquinas))

    maquinas=[]
    for maquina in trt.tarea.get_maquinas_producto(trt.producto):
      if cronograma.has_maquina(maquina):
        maquinas.append(maquina)
    self.assertFalse(trt.maquina in maquinas, '%s not in %s' % (trt.maquina, maquinas))
        
    maquinas = cronograma.get_maquinas_tarea_producto(trt.tarea, trt.producto)
    self.assertFalse(trt.maquina in maquinas, '%s not in %s' % (trt.maquina, maquinas))

    cronograma.planificar()

    self.verificar_cantidad_planificada(cronograma)

    for x in TiempoRealizacionTarea.objects.filter(activa=False):
      intervalos_con_maquinas_inactivas = cronograma.intervalocronograma_set.filter(
        maquina=x.maquina, producto=x.producto, tarea=x.tarea)

      self.assertEqual(intervalos_con_maquinas_inactivas.count(),0)

class CargaAutomaticaDeMaquinasEnCronograma(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/planificar_sin_todas_las_maquinas.json' ]

  def setUp(self):
    self.cronograma = Cronograma(descripcion='Carga Automática de Maquinas')
    self.cronograma.clean()
    self.cronograma.save()

    post_save.connect(add_maquinas_posibles_to_cronograma, 
      sender=PedidoCronograma)
    for pedido in PedidoPlanificable.objects.all():
      self.cronograma.add_pedido(pedido)
    post_save.disconnect(add_maquinas_posibles_to_cronograma, 
      sender=PedidoCronograma)

  def test_planificar_sin_todas_las_maquinas(self):

    maquinas_cronograma = self.cronograma.get_maquinas()

    for pedido in self.cronograma.get_pedidos():
      for maquina in pedido.get_maquinas_posibles_produccion():
        self.assertIn(maquina,maquinas_cronograma)

class ActivacionCronogramaTestCase(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/dos_cronogramas.json' ]

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

  fixtures = [ 'planificacion/fixtures/tests/planificar_con_maquinas_inactivas.json' ]

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

  fixtures = [ 'planificacion/fixtures/tests/planificar_con_maquinas_inactivas.json' ]

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


class PlanificacionSoloLunesDe8A12TestCase(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/planificar_con_maquinas_inactivas.json' ]

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

  fixtures = [ 'planificacion/fixtures/tests/planificar_con_calendario.json' ]

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

class PlanificacionConCalendarioTestCase(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/planificar_con_calendario.json' ]

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

class EstadoCronogramaIntervalosTestCase(PlanificacionConCalendarioTestCase):

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

    # Se verifica que la cantidad de intervalos planificados del pedido de
    # neumáticos de autos sea igual a la cantidad de intervalos cancelados
    pedido_neumaticos = self.crono_solo_neumaticos.get_pedidos()[0]
    self.assertEqual(
      self.crono_todo.intervalocronograma_set.filter(
        pedido=pedido_neumaticos).count(),
      self.crono_solo_neumaticos.intervalocronograma_set.filter(
        estado=ESTADO_INTERVALO_CANCELADO).count())

class DeberiaDejarCancelarIntervalo60(PlanificadorTestCase):
  
  fixtures = [ 'planificacion/fixtures/tests/deberia_dejar_cancelar_intervalo_60.json' ]
  
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

class PlanificacionPedidoTestCase(PlanificacionConCalendarioTestCase):

  def setUp(self):
    
    Cronograma.objects.all().delete()
  
  def test_planificar_pedido(self):

    pedido = PedidoPlanificable.objects.all()[0]

    self.assertTrue(pedido.is_pendiente_planificar())

    crono1 = pedido.planificar()
    self.assertTrue(pedido.is_planificado())
    self.verificar_cantidad_planificada(crono1)

    self.assertRaises(EstadoPedidoError, pedido.finalizar)
    self.assertRaises(EstadoPedidoError, pedido.cancelar)

    crono1.activar()
    self.assertTrue(pedido.is_activo())

    self.assertRaises(EstadoPedidoError, pedido.planificar)

    intervalos = [ i for i in pedido.get_intervalos_ordenados_por_dependencia() ]
    intervalos[0].cancelar()
    self.assertTrue(pedido.is_pendiente_planificar())

    crono2 = pedido.planificar()
    self.assertTrue(pedido.is_planificado())
    self.verificar_cantidad_planificada(crono1)

    crono2.activar()
    self.assertTrue(pedido.is_activo())
    
    intervalos = [ i for i in pedido.get_intervalos_ordenados_por_dependencia() ]

    intervalo_cancelado = intervalos[len(intervalos)/2]
    intervalo_cancelado.cancelar()
    self.assertTrue(pedido.is_pendiente_planificar())

    pedido.finalizar()
    self.assertTrue(pedido.is_pendiente_planificar())

    crono3 = pedido.planificar()
    self.assertTrue(pedido.is_planificado())
    self.verificar_cantidad_planificada(crono3)

    crono3.activar()
    self.assertTrue(pedido.is_activo())
 
    pedido.finalizar()
    self.assertTrue(pedido.is_finalizado())
