# coding=utf-8
from .models import PedidoCronograma, MaquinaPlanificacion
from .dependencias import GerenciadorDependencias
from django.db.models.signals import post_save, post_delete
from django.db.models.signals import pre_delete


def validar_dependencias_borrado(sender, instance, **kwargs):
  gerenciador_dependencias = GerenciadorDependencias.crear_desde_instante(instance)
  gerenciador_dependencias.verificar_eliminar_instante(instance)

#pre_delete.connect(validar_dependencias_borrado, 
  #sender=IntervaloCronograma)

def add_maquinas_posibles_to_cronograma(sender, instance, created, **kwargs):
  if not created:
    return
  if not instance.pedido:
    return
  if not instance.cronograma:
    return
  for maquina in instance.pedido.get_maquinas_posibles_produccion():
    if not instance.cronograma.has_maquina(maquina):
      maquina = MaquinaPlanificacion.fromMaquina(maquina)
      instance.cronograma.add_maquina(maquina)

post_save.connect(add_maquinas_posibles_to_cronograma, 
  sender=PedidoCronograma)

