# coding=utf-8
from django.test import TestCase
from produccion.models import * 
from planificacion.models import * 
import datetime
import pytz

utc=pytz.UTC

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

    cronograma = Cronograma(descripcion='CRON1', intervalo_tiempo=240, estrategia=2)
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

    cronograma = Cronograma(descripcion='CRON1', intervalo_tiempo=240, estrategia=2, 
      fecha_inicio=datetime.datetime(2014,1,1,0,0,0),)

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
    
    intervalo=IntervaloCronograma(cronograma=cronograma,maquina=M1,secuencia=1,
      tarea=T1,producto=P1,pedido=D1,cantidad_tarea=100/5,
      tiempo_intervalo=100)
    intervalo.clean()
    intervalo.save()

    intervalo=IntervaloCronograma(cronograma=cronograma,maquina=M1,secuencia=2,
      tarea=T1,producto=P1,pedido=D1,cantidad_tarea=100/5,
      tiempo_intervalo=100)

    self.assertEqual(len(intervalo.get_intervalos_anteriores_maquina()),1)

    intervalo.calcular_fecha_desde()

    self.assertEqual(intervalo.fecha_desde,utc.localize(datetime.datetime(2014,1,1,1,40,0)))

    intervalo.clean()
    intervalo.save()

    intervalo=IntervaloCronograma(cronograma=cronograma,maquina=M1,secuencia=2,
      tarea=T1,producto=P1,pedido=D1,cantidad_tarea=100/5,
      tiempo_intervalo=100)

    self.assertEqual(len(intervalo.get_intervalos_anteriores_maquina()),1)

    intervalo.calcular_fecha_desde()

    self.assertEqual(intervalo.fecha_desde,utc.localize(datetime.datetime(2014,1,1,1,40,0)))


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

    cronograma = Cronograma(descripcion='CRON1', intervalo_tiempo=240, estrategia=2, 
      fecha_inicio=datetime.datetime(2014,1,1,0,0,0),)

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
    
    # Se agrega una tarea T1 entre [0;25] como resultado da una cantidad de 5
    I1=IntervaloCronograma(cronograma=cronograma,maquina=M1,secuencia=1,
      tarea=T1,producto=P1,pedido=D1,cantidad_tarea=25/5,
      tiempo_intervalo=25)
    I1.clean()
    I1.save()


    # Se planifica I2 en la máquina M2 en la fecha de finalización de I1
    I2=IntervaloCronograma(cronograma=cronograma,maquina=M2,secuencia=1,
      tarea=T2,producto=P1,pedido=D1,cantidad_tarea=100/10,
      tiempo_intervalo=100, fecha_desde=I1.get_fecha_hasta())

    # Se verifica que cuando se asigna la fecha desde, el cálculo no la modifica.
    I2.calcular_fecha_desde()
    self.assertEqual(I2.get_fecha_desde(),I1.get_fecha_hasta())

    # Se verifica que la obtención de los intervalos sea correcta:
    intervalos = GerenciadorDependencias.crear_desde_instante(I2).get_intervalos([T1,T2],instante_agregado=I2)
    self.assertEqual(len(intervalos),2)

    try:
      # como I1:M1:T1:5:[0;25] y I2:M2:T2:10:[25;125] y T1 -> T2 => 
      # => En 75 ya no se puede seguir produciendo T2
      # Por lo tanto debe ocurrir un error.
      I2.clean()
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
      self.fail("No aplico la validacion de cantidad de tarea anterior necesaria para tarea agregada.")
    except ValidationError:
      pass

    # Agregamos el intervalo I3:M1:T1:5:[25;50]
    I3=IntervaloCronograma(cronograma=cronograma,maquina=M1,secuencia=2,
      tarea=T1,producto=P1,pedido=D1,cantidad_tarea=25/5,
      tiempo_intervalo=25)
    I3.clean()
    I3.save()
    
    # Verificamos que la fecha de inicio de I3 coincida con la de I1 finalización de I1:
    self.assertEqual(I3.get_fecha_desde(),I1.get_fecha_hasta())

    # como I1:M1:T1:5:[0;25] y I3:M1:T1:5:[25;50] y I2:M2:T2:10:[0;100] y T1 -> T2 => 
    # Vemos que no hay problemas de dependencia
    I2.clean()
