from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import TareaMaquina, TareaProducto, TiempoRealizacionTarea

def agregar_combinaciones_tiempos(sender, instance, **kwargs):
  """
  Una misma tarea T que este asociada a una maquina M por un lado y a un 
  producto P por el otro debe generar una entrada (T,M,P)
  """
  tarea = instance.tarea

  for tareaMaquina in tarea.tareamaquina_set.all():
    for tareaProducto in tarea.tareaproducto_set.all():
      maquina=tareaMaquina.maquina
      producto=tareaProducto.producto
      try:
        TiempoRealizacionTarea.objects.get(tarea=tarea,
          maquina=maquina, producto=producto)
      except TiempoRealizacionTarea.DoesNotExist:
        TiempoRealizacionTarea.objects.create(tarea=tarea,
          maquina=maquina, producto=producto, tiempo=tarea.tiempo,
          tareamaquina=tareaMaquina, tareaproducto=tareaProducto)

post_save.connect(agregar_combinaciones_tiempos, 
  sender=TareaMaquina)
post_save.connect(agregar_combinaciones_tiempos, 
  sender=TareaProducto)
