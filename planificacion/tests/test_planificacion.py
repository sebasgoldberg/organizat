# coding=utf-8
from .base import *

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

  #@profile
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
      fecha_inicio=utc.localize(datetime.datetime(2014,1,1,0,0,0)),tiempo_minimo_intervalo=0)

    cronograma.clean()
    cronograma.save()

    cronograma.add_maquina(M1)
    cronograma.add_maquina(M2)
    cronograma.add_maquina(M3)

    cronograma.add_pedido(D1)
    cronograma.add_pedido(D2)
    cronograma.add_pedido(D3)

  #@profile
  def test_calcular_fecha_desde(self):
    
    cronograma = Cronograma.objects.get(descripcion='CRON1')
    M1 = MaquinaPlanificacion.objects.get(descripcion='M1')
    T1 = Tarea.objects.get(descripcion='T1')
    P1 = Producto.objects.get(descripcion='P1')
    D1 = PedidoPlanificable.objects.get(descripcion='D1')
    I1 = D1.get_item_producto(P1)
    
    intervalo=IntervaloCronograma(cronograma=cronograma,maquina=M1,
      tarea=T1,item=I1,cantidad_tarea=100/5,
      tiempo_intervalo=100)
    intervalo.clean()
    intervalo.save()

    intervalo=IntervaloCronograma(cronograma=cronograma,maquina=M1,
      tarea=T1,item=I1,cantidad_tarea=100/5,
      tiempo_intervalo=100)
    intervalo.clean()

    self.assertEqual(intervalo.fecha_desde,utc.localize(datetime.datetime(2014,1,1,1,40,0)))

    intervalo.save()

    fecha_hasta = intervalo.get_fecha_hasta()
    intervalo=IntervaloCronograma(cronograma=cronograma,maquina=M1,
      tarea=T1,item=I1,cantidad_tarea=100/5,
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
      fecha_inicio=utc.localize(datetime.datetime(2014,1,1,0,0,0)), tiempo_minimo_intervalo=0)

    cronograma.clean()
    cronograma.save()

    cronograma.add_maquina(M1)
    cronograma.add_maquina(M2)

    cronograma.add_pedido(D1)

    P1.add_dependencia_tareas(tarea_anterior=T1,tarea=T2)

  #@profile
  def test_calcular_fecha_desde(self):
    
    cronograma = Cronograma.objects.get(descripcion='CRON1')
    M1 = MaquinaPlanificacion.objects.get(descripcion='M1')
    M2 = MaquinaPlanificacion.objects.get(descripcion='M2')
    T1 = Tarea.objects.get(descripcion='T1')
    T2 = Tarea.objects.get(descripcion='T2')
    P1 = Producto.objects.get(descripcion='P1')
    D1 = PedidoPlanificable.objects.get(descripcion='D1')
    itemP1 = D1.get_item_producto(P1)

    # Se verifica la obtención de tareas ordenadas por grado de dependencia
    tareas_ordenadas_por_grado_dependencia=P1.get_tareas_ordenadas_por_dependencia()
    self.assertEqual(tareas_ordenadas_por_grado_dependencia[0].id,T1.id)
    self.assertEqual(tareas_ordenadas_por_grado_dependencia[1].id,T2.id)
    
    # Se agrega una tarea T1 entre [0;25] como resultado da una cantidad de 5
    I1=IntervaloCronograma(cronograma=cronograma,maquina=M1,
      tarea=T1,item=itemP1,cantidad_tarea=25/5,
      tiempo_intervalo=25, fecha_desde=cronograma.fecha_inicio)
    I1.clean()
    I1.save()


    # Se planifica I2 en la máquina M2 en la fecha de finalización de I1
    I2=IntervaloCronograma(cronograma=cronograma,maquina=M2,
      tarea=T2,item=itemP1,cantidad_tarea=100/10,
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
      tarea=T1,item=itemP1,cantidad_tarea=25/5,
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
      tarea=T2,item=itemP1,cantidad_tarea=100/10,
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
      fecha_inicio=utc.localize(datetime.datetime(2014,1,1,0,0,0)),)

    cronograma.clean()
    cronograma.save()

    cronograma.add_maquina(M1)
    cronograma.add_maquina(M2)

    cronograma.add_pedido(D1)

    P1.add_dependencia_tareas(tarea_anterior=T2,tarea=T1)

  #@profile
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
  
  fixtures = [ getFixture('hueco_inexplicable.json') ]

  #@profile
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

  fixtures = [ getFixture('hueco_inexplicable.json') ]

  def setUp(self):

    # Se recupera el primero, porque hay un solo cronograma definido.
    cronograma = Cronograma.objects.get(pk=1)

    cronograma.planificar()

  #@profile
  def test_tiempo_minimo_bloque(self):

    cronograma = Cronograma.objects.get(pk=1)

    for intervalo in cronograma.intervalocronograma_set.all():
      self.assertLessEqual(intervalo.cronograma.tiempo_minimo_intervalo,intervalo.tiempo_intervalo,
        u'El intervalo %s tiene un tiempo %s menor al tiempo mínimo %s.' % (
          intervalo, intervalo.tiempo_intervalo, intervalo.cronograma.tiempo_minimo_intervalo))

class TiempoMenorAlTiempoMinimoTestCase(PlanificadorTestCase):

  fixtures = [ getFixture('hueco_inexplicable.json') ]

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

  #@profile
  def test_tiempo_menor_al_tiempo_minimo(self):

    cronograma = Cronograma.objects.get(pk=1)

    tiempo_minimo_intervalo = cronograma.tiempo_minimo_intervalo

    cronograma.planificar()

    # Tomamos cualquier intervalo del pedido D4
    intervalo = IntervaloCronograma.objects.filter(item__pedido__descripcion='D4').first()

    # Verificamos que el intervalo tiene una duración menor a la del tiempo mínimo
    self.assertLess(intervalo.tiempo_intervalo,tiempo_minimo_intervalo)

class PlanificarSinHuecosEvitables(PlanificadorTestCase):

  fixtures = [ getFixture('hueco_inexplicable.json') ]

  def setUp(self):

    cronograma = Cronograma.objects.get(pk=1)

    cronograma.tiempo_minimo_intervalo = 0
    cronograma.clean()
    cronograma.save()
    cronograma.planificar()

  #@profile
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

  fixtures = [ getFixture('mas_de_una_dependencia.json') ]

  def setUp(self):

    cronograma = Cronograma.objects.get(pk=1)

    cronograma.clean()
    cronograma.save()
    cronograma.planificar()

  #@profile
  def test_cantidad_planificada(self):
    
    cronograma = Cronograma.objects.get(pk=1)

    self.verificar_cantidad_planificada(cronograma)


class MasDeUnaDependencia120ErrorOperacion(PlanificadorTestCase):

  fixtures = [ getFixture('mas_de_una_dependencia.json') ]

  def setUp(self):

    cronograma = Cronograma.objects.get(pk=1)

    cronograma.tiempo_minimo_intervalo = 120
    cronograma.clean()
    cronograma.save()
    cronograma.planificar()

  #@profile
  def test_cantidad_planificada(self):
    
    cronograma = Cronograma.objects.get(pk=1)

    self.verificar_cantidad_planificada(cronograma)

class DosCronogramasTestCase(PlanificadorTestCase):

  fixtures = [ getFixture('dos_cronogramas.json') ]

  #@profile
  def test_cantidad_planificada(self):
    
    cronograma = Cronograma.objects.get(descripcion='Otro crono')

    cronograma.clean()
    cronograma.save()
    cronograma.planificar()

    self.verificar_cantidad_planificada(cronograma)

class PlanificarSinTodasLasMaquinas(PlanificadorTestCase):

  fixtures = [ getFixture('planificar_sin_todas_las_maquinas.json') ]

  #@profile
  def test_planificar_sin_todas_las_maquinas(self):

    cronograma = Cronograma.objects.get(descripcion='Solo neumáticos de auto')

    cronograma.planificar()

    self.verificar_cantidad_planificada(cronograma)


class PlanificarConMaquinasInactivas(PlanificadorTestCase):

  fixtures = [ getFixture('planificar_con_maquinas_inactivas.json') ]

  #@profile
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
        maquina=x.maquina, item__producto=x.producto, tarea=x.tarea)

      self.assertEqual(intervalos_con_maquinas_inactivas.count(),0)

class CargaAutomaticaDeMaquinasEnCronograma(PlanificadorTestCase):

  fixtures = [ getFixture('planificar_sin_todas_las_maquinas.json') ]

  def setUp(self):
    self.cronograma = Cronograma(descripcion='Carga Automática de Maquinas')
    self.cronograma.clean()
    self.cronograma.save()

    for pedido in PedidoPlanificable.objects.all():
      self.cronograma.add_pedido(pedido)

  #@profile
  def test_planificar_sin_todas_las_maquinas(self):

    maquinas_cronograma = self.cronograma.get_maquinas()

    for pedido in self.cronograma.get_pedidos():
      for maquina in pedido.get_maquinas_posibles_produccion():
        self.assertIn(maquina,maquinas_cronograma)


class StandsTestCase(TestCase):

    #@profile
    def test_stand_loreal(self):
        """
        Esta prueba surje de demostrar la mejora inmediata que se 
        da en caso que uno particione los productos de un pedido en
        varios items. El tiempo de ejecución de este caso, sin partición 
        alguna crecería en forma exponencial.
        """

        calendario = CalendarioProduccion.get_instance()

        # se define calendario lu a vi de 8 a 8:30
        calendario.add_intervalos_laborables(
          dias_laborables=[DiaSemana.LUNES,DiaSemana.MARTES,
            DiaSemana.MIERCOLES,DiaSemana.JUEVES,DiaSemana.VIERNES],
          hora_desde=T(8), hora_hasta=T(12))

        producto = Producto.objects.create(descripcion='Stand Loreal')

        tarea_armado = Tarea.objects.create(
            descripcion='Armado', tiempo=180)
        tarea_embalaje = Tarea.objects.create(
            descripcion='Embalaje', tiempo=90)
        tarea_grafica_cenefas = Tarea.objects.create(
            descripcion='Grafica Cenefas', tiempo=120)
        tarea_pintura = Tarea.objects.create(
            descripcion='Pintura', tiempo=240)
        tarea_termoformado = Tarea.objects.create(
            descripcion='Termoformado', tiempo=30)

        maquina_mano_obra = Maquina.objects.create(descripcion='Mano de Obra')
        maquina_plotter = Maquina.objects.create(descripcion='Plotter')
        maquina_cabina_pintura = Maquina.objects.create(descripcion='Cabina Pintura')
        maquina_termoformadora_1 = Maquina.objects.create(descripcion='Termoformadora 1')
        maquina_termoformadora_2 = Maquina.objects.create(descripcion='Termoformadora 2')

        maquina_mano_obra.add_tarea(tarea_armado)
        maquina_mano_obra.add_tarea(tarea_embalaje)
        maquina_plotter.add_tarea(tarea_grafica_cenefas)
        maquina_cabina_pintura.add_tarea(tarea_pintura)
        maquina_termoformadora_1.add_tarea(tarea_termoformado)
        maquina_termoformadora_2.add_tarea(tarea_termoformado)

        producto.add_tarea(tarea_armado)
        producto.add_tarea(tarea_embalaje)
        producto.add_tarea(tarea_grafica_cenefas)
        producto.add_tarea(tarea_pintura)
        producto.add_tarea(tarea_termoformado)

        producto.add_dependencia_tareas(
            tarea_anterior=tarea_grafica_cenefas, tarea=tarea_armado)
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_pintura, tarea=tarea_armado)
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_armado, tarea=tarea_embalaje)
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_termoformado, tarea=tarea_grafica_cenefas)
        producto.add_dependencia_tareas(
            tarea_anterior=tarea_termoformado, tarea=tarea_pintura)

        pedido = PedidoPlanificable.objects.create()
        pedido.add_item(producto,7)

        cronograma = pedido.crear_cronograma()

        cronograma.planificar()

