# coding=utf-8
from django.test import TestCase
from produccion.models import * 
from planificacion.models import * 
import datetime
import pytz
from django.db.transaction import rollback
from django.utils.translation import ugettext as _

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

    M1=Maquina.objects.create(descripcion='M1')
    M2=Maquina.objects.create(descripcion='M2')
    M3=Maquina.objects.create(descripcion='M3')

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

    D1=Pedido.objects.create(descripcion='D1')
    D2=Pedido.objects.create(descripcion='D2')
    D3=Pedido.objects.create(descripcion='D3')

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

    M1=Maquina.objects.create(descripcion='M1')
    M2=Maquina.objects.create(descripcion='M2')
    M3=Maquina.objects.create(descripcion='M3')

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

    D1=Pedido.objects.create(descripcion='D1')
    D2=Pedido.objects.create(descripcion='D2')
    D3=Pedido.objects.create(descripcion='D3')

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
    M1 = Maquina.objects.get(descripcion='M1')
    T1 = Tarea.objects.get(descripcion='T1')
    P1 = Producto.objects.get(descripcion='P1')
    D1 = Pedido.objects.get(descripcion='D1')
    
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

    M1=Maquina.objects.create(descripcion='M1')
    M2=Maquina.objects.create(descripcion='M2')

    T1=Tarea.objects.create(descripcion='T1', tiempo=5)
    T2=Tarea.objects.create(descripcion='T2', tiempo=10)

    TareaMaquina.objects.create(tarea=T1,maquina=M1)
    TareaMaquina.objects.create(tarea=T2,maquina=M2)

    P1=Producto.objects.create(descripcion='P1')

    TareaProducto.objects.create(tarea=T1,producto=P1)
    TareaProducto.objects.create(tarea=T2,producto=P1)

    D1=Pedido.objects.create(descripcion='D1')

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
    M1 = Maquina.objects.get(descripcion='M1')
    M2 = Maquina.objects.get(descripcion='M2')
    T1 = Tarea.objects.get(descripcion='T1')
    T2 = Tarea.objects.get(descripcion='T2')
    P1 = Producto.objects.get(descripcion='P1')
    D1 = Pedido.objects.get(descripcion='D1')

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
    intervalos = GerenciadorDependencias.crear_desde_instante(I2).get_intervalos([T1,T2],instante_agregado=I2)
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
    intervalos = gd.get_intervalos([T1,T2],instante_borrado=I3)
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

    M1=Maquina.objects.create(descripcion='M1')
    M2=Maquina.objects.create(descripcion='M2')

    T1=Tarea.objects.create(descripcion='T1', tiempo=5)
    T2=Tarea.objects.create(descripcion='T2', tiempo=10)

    TareaMaquina.objects.create(tarea=T1,maquina=M1)
    TareaMaquina.objects.create(tarea=T2,maquina=M2)

    P1=Producto.objects.create(descripcion='P1')

    TareaProducto.objects.create(tarea=T1,producto=P1)
    TareaProducto.objects.create(tarea=T2,producto=P1)

    D1=Pedido.objects.create(descripcion='D1')

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
    D1 = Pedido.objects.get(descripcion='D1')
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

    # Se verifica el correcto funcionamiento de la obtención de huecos.
    for maquina in Maquina.objects.all():
      huecos = cronograma.get_huecos(maquina)
      intervalo_anterior = None
      intervalos = IntervaloCronograma.objects.filter(maquina=maquina).order_by('fecha_desde')
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
        hueco_encontrado = False
        for hueco in huecos:
          if hueco.fecha_desde == fecha_desde and\
            hueco.get_fecha_hasta() == fecha_hasta:
            hueco_encontrado = True
            break
        self.assertTrue(hueco_encontrado,"Huecos: %s;\n Intervalos: %s;\n desde: %s;\n hasta: %s" % (
          [h.__unicode__() for h in huecos], [i for i in intervalos], fecha_desde, fecha_hasta) )

    M3 = Maquina.objects.get(descripcion='M3')
    huecos = cronograma.get_huecos(M3)

    if len(huecos) == 0:
      return

    self.assertEqual(len(huecos),1)

    hueco = huecos[0]

    self.assertLess(hueco.fecha_desde,hueco.get_fecha_hasta())

    # Se obtiene el intervalo posterior al hueco.
    intervalo = IntervaloCronograma.objects.get(maquina=M3, fecha_desde=hueco.get_fecha_hasta()) 

    intervalo.fecha_desde = hueco.fecha_desde
    intervalo.clean()
    intervalo.save()

    # Se borra el intervalo y se agrega al final.
    intervalo.delete()
    intervalo.id = None
    gerenciador_dependencias = GerenciadorDependencias.crear_desde_instante(intervalo)
    nuevo_intervalo = gerenciador_dependencias.crear_intervalo_al_final(
      intervalo.maquina, intervalo.tarea, intervalo.tiempo_intervalo)
    self.assertEqual(nuevo_intervalo.fecha_desde, hueco.fecha_desde)
    #self.fail('Se pudo tapar el hueco moviendo el intervalo, pero esto debería haber sido planificado desde un principio.')

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

    pedido=Pedido(descripcion='D4')
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


class CronogramaMaquinaTestCase(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/dos_cronogramas.json' ]

  def get_cronogramas(self):
    return Cronograma.objects.filter(descripcion__in=['Crono pedidos B y C','Otro crono'])

  def setUp(self):

    # @todo Descomentar una vez que aplique el cronograma activo
    return
    
    for cronograma in self.get_cronogramas():
      cronograma.planificar()

  def test_no_permitir_multiples_cronogramas(self):

    # @todo Descomentar una vez que aplique el cronograma activo
    return

    self.assertEqual(CronogramaActivo.objects.count(),1)

    self.assertEqual(CronogramaActivo.get_instance().pedidocronograma_set.count(),0)
    
    self.assertEqual(CronogramaActivo.get_instance().intervalocronograma_set.count(),0)

    cronogramas = self.get_cronogramas()

    crono1 = cronogramas[0]
    crono2 = cronogramas[1]

    crono1.distribuir()

    try:
      crono1.distribuir()
      self.fail(u'No debería permitir distribuir un cronograma que referencia a pedidos ya distribuidos.')
    except PedidoYaDistribuido:
      pass

    try:
      crono2.distribuir()
      self.fail(u'No debería permitir distribuir un cronograma que referencia a pedidos ya distribuidos.')
    except PedidoYaDistribuido:
      pass

    self.verificar_cantidad_planificada(CronogramaActivo.get_instance())


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

class CargaAutomaticaDeMaquinasEnCronograma(TestCase):

  fixtures = [ 'planificacion/fixtures/tests/planificar_sin_todas_las_maquinas.json' ]

  def setUp(self):
    
    self.cronograma = Cronograma(descripcion='Carga Automática de Maquinas')
    self.cronograma.clean()
    self.cronograma.save()

    for pedido in Pedido.objects.all():
      self.cronograma.add_pedido(pedido)

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
    IntervaloCronograma.objects.all().delete()
    self.c1.activar()
    self.c2.planificar()
    self.validar_no_existe_solapamiento()

  def test_activo_c2_planifico_c1(self):
    IntervaloCronograma.objects.all().delete()
    self.c2.activar()
    self.c1.planificar()
    self.validar_no_existe_solapamiento()

  def test_activo_todo(self):
    IntervaloCronograma.objects.all().delete()
    self.c2.activar()
    self.c1.activar()
    self.validar_no_existe_solapamiento()

  def test_planifico_luego_activo(self):
    IntervaloCronograma.objects.all().delete()
    self.c2.planificar()
    self.c1.planificar()
    self.c2.activar()

    self.c1 = Cronograma.objects.get(descripcion="Crono pedidos B y C")
    self.assertFalse(self.c1.is_valido())

    self.c1.activar()
    self.validar_no_existe_solapamiento()

  def validar_no_existe_solapamiento(self):
    """
    Se verifica que no existan solapamientos.
    """
    for maquina in Maquina.objects.all():
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

    algun_producto_del_cronograma = cronograma.get_pedidos()[0].get_items()[0].producto

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

    intervalo_dependiente.cantidad_tarea_real = intervalo_primer_grado.cantidad_tarea / 2
    try:
      intervalo_dependiente.clean()
      self.fail(_(u'La cantidad de tarea real en el intervalo %s supera la cantidad de tarea real en el intervalo %s.') % (
        intervalo_dependiente, intervalo_primer_grado))
    except TareaRealNoRespetaDependencias:
      pass

    intervalo_primer_grado.cantidad_tarea_real = intervalo_primer_grado.cantidad_tarea / 2
    intervalo_primer_grado.clean()
    intervalo_primer_grado.save()

    intervalo_dependiente.cantidad_tarea_real = intervalo_primer_grado.cantidad_tarea / 2
    intervalo_dependiente.clean()
    intervalo_dependiente.save()

    intervalo_primer_grado.cantidad_tarea_real = intervalo_primer_grado.cantidad_tarea_real - 1
    try:
      intervalo_primer_grado.clean()
      self.fail(_(u'La cantidad de tarea real en el intervalo %s supera la cantidad de tarea real en el intervalo %s.') % (
        intervalo_dependiente, intervalo_primer_grado))
    except TareaRealNoRespetaDependencias:
      pass

    try:
      cronograma.desactivar()
      self.fail(_(u'No debería poder desactivarse un cronograma que tiene intervalos con cantidad de tarea real.'))
    except TareaRealEnCronogramaInactivo:
      pass

class EstadoIntervaloCronogramaTestCase(PlanificadorTestCase):

  fixtures = [ 'planificacion/fixtures/tests/planificar_con_maquinas_inactivas.json' ]

  def test_validaciones_finalizar_cancelar_intervalo(self):

    IntervaloCronograma.objects.all().delete()

    cronograma = Cronograma.objects.get(descripcion='Solo neumáticos de auto')

    algun_producto_del_cronograma = cronograma.get_pedidos()[0].get_items()[0].producto

    tarea_primer_grado = algun_producto_del_cronograma.get_tareas_ordenadas_por_dependencia()[0]

    cronograma.planificar()

    intervalo_primer_grado = IntervaloCronograma.objects.filter(cronograma=cronograma, 
      tarea=tarea_primer_grado).order_by('fecha_desde').first()

    try:
      intervalo_primer_grado.finalizar(intervalo_primer_grado.cantidad_tarea / 2)
      self.fail(_(u'No debería ser posible finalizar un intervalo perteneciente a un cronograma inactivo.'))
    except IntervaloFinalizadoEnCronogramaInactivo:
      pass

    try:
      intervalo_primer_grado.iniciar()
      self.fail(_(u'No debería ser posible iniciar un intervalo perteneciente a un cronograma inactivo.'))
    except IntervaloEnCursoEnCronogramaInactivo:
      pass

    try:
      intervalo_primer_grado.cancelar()
      self.fail(_(u'No debería ser posible cancelar un intervalo perteneciente a un cronograma inactivo.'))
    except IntervaloCanceladoEnCronogramaInactivo:
      pass

    cronograma.activar()

    cronograma.desactivar()

    cronograma.activar()

    intervalo_primer_grado = IntervaloCronograma.objects.filter(cronograma=cronograma, 
      tarea=tarea_primer_grado).order_by('fecha_desde').first()

    try:
      intervalo_primer_grado.finalizar()
      self.fail(_(u'No debería ser posible finalizar un intervalo con cantidad real nula'))
    except IntervaloFinalizadoConCantidadNula:
      pass

    intervalo_primer_grado.finalizar(intervalo_primer_grado.cantidad_tarea / 2)

    intervalo_primer_grado = IntervaloCronograma.objects.filter(cronograma=cronograma, 
      tarea=tarea_primer_grado).order_by('fecha_desde').first()

    self.assertEqual(intervalo_primer_grado.estado, ESTADO_INTERVALO_FINALIZADO)
    self.assertEqual(intervalo_primer_grado.cantidad_tarea_real, intervalo_primer_grado.cantidad_tarea / 2)

    try:
      intervalo_primer_grado.estado = ESTADO_INTERVALO_CANCELADO
      intervalo_primer_grado.clean()
      self.fail(_(u'No debería ser posible cancelar un intervalo con cantidad real mayor a cero.'))
    except IntervaloCanceladoConCantidadNoNula:
      pass

    intervalo_primer_grado = IntervaloCronograma.objects.filter(cronograma=cronograma, 
      tarea=tarea_primer_grado).order_by('fecha_desde').first()

    intervalo_primer_grado.cancelar()

    self.assertEqual(intervalo_primer_grado.estado, ESTADO_INTERVALO_CANCELADO)
    self.assertEqual(intervalo_primer_grado.cantidad_tarea_real, 0)

    try:
      cronograma.desactivar()
      self.fail(_(u'No debería poder desactivarse un cronograma que tiene intervalos con estado distinto de planificado.'))
    except IntervaloDistintoPlanificadoEnCronogramaInactivo:
      pass
