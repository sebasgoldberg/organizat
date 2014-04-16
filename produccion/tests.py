# coding=utf-8
from django.test import TestCase
from produccion.models import * 
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError

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

  def test_completado_automatico_tiempos(self):
    """
    Dadas las condiciones iniciales en el método setUp, el modelo
    TiempoRealizacionTarea debería tener solo las siguientes
    instancias (12 en total):
      (M1,T1,P1, 5)
      (M1,T1,P2, 5)
      (M1,T1,P3, 5)
      (M2,T1,P1, 5)
      (M2,T1,P2, 5)
      (M2,T1,P3, 5)
      (M2,T2,P1, 10)
      (M2,T2,P3, 10)
      (M3,T2,P1, 10)
      (M3,T2,P3, 10)
      (M3,T3,P2, 3.5)
      (M3,T3,P3, 3.5)
    """
    self.assertEqual(TiempoRealizacionTarea.objects.count(),12)

    M1=Maquina.objects.get(descripcion='M1')
    M2=Maquina.objects.get(descripcion='M2')
    M3=Maquina.objects.get(descripcion='M3')
    T1=Tarea.objects.get(descripcion='T1')
    T2=Tarea.objects.get(descripcion='T2')
    T3=Tarea.objects.get(descripcion='T3')
    P1=Producto.objects.get(descripcion='P1')
    P2=Producto.objects.get(descripcion='P2')
    P3=Producto.objects.get(descripcion='P3')

    TiempoRealizacionTarea.objects.get(maquina=M1, tarea=T1, producto=P1, tiempo=5)
    TiempoRealizacionTarea.objects.get(maquina=M1, tarea=T1, producto=P2, tiempo=5)
    TiempoRealizacionTarea.objects.get(maquina=M1, tarea=T1, producto=P3, tiempo=5)
    TiempoRealizacionTarea.objects.get(maquina=M2, tarea=T1, producto=P1, tiempo=5)
    TiempoRealizacionTarea.objects.get(maquina=M2, tarea=T1, producto=P2, tiempo=5)
    TiempoRealizacionTarea.objects.get(maquina=M2, tarea=T1, producto=P3, tiempo=5)
    TiempoRealizacionTarea.objects.get(maquina=M2, tarea=T2, producto=P1, tiempo=10)
    TiempoRealizacionTarea.objects.get(maquina=M2, tarea=T2, producto=P3, tiempo=10)
    TiempoRealizacionTarea.objects.get(maquina=M3, tarea=T2, producto=P1, tiempo=10)
    TiempoRealizacionTarea.objects.get(maquina=M3, tarea=T2, producto=P3, tiempo=10)
    TiempoRealizacionTarea.objects.get(maquina=M3, tarea=T3, producto=P2, tiempo=3.5)
    TiempoRealizacionTarea.objects.get(maquina=M3, tarea=T3, producto=P3, tiempo=3.5)

    """
    Luego de borrar la maquina M2 deberían quedar las siguientes relaciones:
      (M1,T1,P1, 5)
      (M1,T1,P2, 5)
      (M1,T1,P3, 5)
      (M3,T2,P1, 10)
      (M3,T2,P3, 10)
      (M3,T3,P2, 3.5)
      (M3,T3,P3, 3.5)
    """
    M2.delete()

    self.assertEqual(TiempoRealizacionTarea.objects.count(),7)

    TiempoRealizacionTarea.objects.get(maquina=M1, tarea=T1, producto=P1, tiempo=5)
    TiempoRealizacionTarea.objects.get(maquina=M1, tarea=T1, producto=P2, tiempo=5)
    TiempoRealizacionTarea.objects.get(maquina=M1, tarea=T1, producto=P3, tiempo=5)
    TiempoRealizacionTarea.objects.get(maquina=M3, tarea=T2, producto=P1, tiempo=10)
    TiempoRealizacionTarea.objects.get(maquina=M3, tarea=T2, producto=P3, tiempo=10)
    TiempoRealizacionTarea.objects.get(maquina=M3, tarea=T3, producto=P2, tiempo=3.5)
    TiempoRealizacionTarea.objects.get(maquina=M3, tarea=T3, producto=P3, tiempo=3.5)

    """
    Luego de borrar la asociacion entre el producto P1 y la tarea T1 deberían 
    quedar las siguientes relaciones:
      (M1,T1,P2, 5)
      (M1,T1,P3, 5)
      (M3,T2,P1, 10)
      (M3,T2,P3, 10)
      (M3,T3,P2, 3.5)
      (M3,T3,P3, 3.5)
    """
    TareaProducto.objects.filter(tarea=T1,producto=P1).delete()

    self.assertEqual(TiempoRealizacionTarea.objects.count(),6)

    TiempoRealizacionTarea.objects.get(maquina=M1, tarea=T1, producto=P2, tiempo=5)
    TiempoRealizacionTarea.objects.get(maquina=M1, tarea=T1, producto=P3, tiempo=5)
    TiempoRealizacionTarea.objects.get(maquina=M3, tarea=T2, producto=P1, tiempo=10)
    TiempoRealizacionTarea.objects.get(maquina=M3, tarea=T2, producto=P3, tiempo=10)
    TiempoRealizacionTarea.objects.get(maquina=M3, tarea=T3, producto=P2, tiempo=3.5)
    TiempoRealizacionTarea.objects.get(maquina=M3, tarea=T3, producto=P3, tiempo=3.5)


class DependenciaTareaProductoTestCase(TestCase):

  def setUp(self):
    P1=Producto.objects.create(descripcion='P1')
    P2=Producto.objects.create(descripcion='P2')

    T1=Tarea.objects.create(descripcion='T1', tiempo=5)
    T2=Tarea.objects.create(descripcion='T2', tiempo=10)
    T3=Tarea.objects.create(descripcion='T3', tiempo=3.5)
    T4=Tarea.objects.create(descripcion='T4', tiempo=6)
    T5=Tarea.objects.create(descripcion='T5', tiempo=7)

    """
          T1    T2    T3    T4    T5
    P1    X     X     X     X
    P2    X     X                 X
    """
    TareaProducto.objects.create(tarea=T1,producto=P1)
    TareaProducto.objects.create(tarea=T2,producto=P1)
    TareaProducto.objects.create(tarea=T3,producto=P1)
    TareaProducto.objects.create(tarea=T4,producto=P1)
    TareaProducto.objects.create(tarea=T1,producto=P2)
    TareaProducto.objects.create(tarea=T2,producto=P2)
    TareaProducto.objects.create(tarea=T5,producto=P2)

  def test_verificacion_dependencia_circular(self):

    P1=Producto.objects.get(descripcion='P1')
    P2=Producto.objects.get(descripcion='P2')

    T1=Tarea.objects.get(descripcion='T1')
    T2=Tarea.objects.get(descripcion='T2')
    T3=Tarea.objects.get(descripcion='T3')
    T4=Tarea.objects.get(descripcion='T4')
    T5=Tarea.objects.get(descripcion='T5')

    """
    Se intenta crear la dependencia T1 -> T5 para el producto P1, pero la
    tarea T5 no forma parte del proceso de producción de P1
    """
    try:
      P1T1T5=DependenciaTareaProducto(producto=P1, tarea_anterior=T1, tarea=T5)
      P1T1T5.clean()
      self.fail('No debería dejar crear dependencias entre tareas que no componen un producto.')
    except ValidationError:
      pass

    """
    Para el producto P1 se crean las dependencias:
      T1 -> T4
      T3 -> T4
      T4 -> T2
    Para el producto P2 se crean las dependencias:
      T2 -> T1
    """
    P1T1T4=DependenciaTareaProducto(producto=P1, tarea_anterior=T1, tarea=T4)
    P1T1T4.clean()
    P1T1T4.save()
    P1T3T4=DependenciaTareaProducto(producto=P1, tarea_anterior=T3, tarea=T4)
    P1T3T4.clean()
    P1T3T4.save()
    P1T4T2=DependenciaTareaProducto(producto=P1, tarea_anterior=T4, tarea=T2)
    P1T4T2.clean()
    P1T4T2.save()

    P2T2T1=DependenciaTareaProducto(producto=P2, tarea_anterior=T2, tarea=T1)
    P2T2T1.clean()
    P2T2T1.save()

    """
    Luego al crear la dependencia T2 -> T1 para el producto P1
    debería ocurrir una excepción.
    """
    try:
      dependencia=DependenciaTareaProducto(producto=P1, tarea_anterior=T2, tarea=T1)
      dependencia.clean()
      self.fail(_(u'Falló la validación de referencia circular.'))
    except ValidationError as e:
      self.assertEqual('Dependencia circular detectada: T2 -> T1 -> T4 -> T2',e.message)

    self.assertEqual(DependenciaTareaProducto.objects.count(),4)
