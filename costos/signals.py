# coding=utf-8
from decimal import Decimal as D
from django.db.models import signals
from produccion.models import Maquina
from costos.models import CostoMaquina
from planificacion.models import (
        IntervaloCronograma,
        Cronograma)
from planificacion.models import cronograma_planificado

def crear_maquina_costo(sender, instance, created, raw, using,
        update_fields, *args, **kwargs):
    if not issubclass(sender, Maquina):
        return
    if raw:
        return
    if instance.costomaquina_set.all().exists():
        return
    CostoMaquina.objects.create(maquina=instance)


def crear_costo_intervalo(sender, instance, created, raw, using,
        update_fields, *args, **kwargs):
    if raw:
        return
    if instance.costointervalo_set.all().exists():
        return
    costomaq = instance.maquina.costomaquina_set.first()
    costo = (D(instance.get_duracion().total_seconds() / 3600) *
        costomaq.costo_por_hora)
    instance.costointervalo_set.create(costo=costo)


def asignar_costo_cronograma(sender, instance, *args, **kwargs):
    if instance.costocronograma_set.exists():
        costocrono = instance.costocronograma_set.first()
    else:
        costocrono = instance.costocronograma_set.create()
    costocrono.costo = 0
    for i in instance.get_intervalos():
        costocrono.costo += i.costointervalo_set.first().costo
    costocrono.clean()
    costocrono.save()


signals.post_save.connect(crear_maquina_costo)

signals.post_save.connect(crear_costo_intervalo,
        sender=IntervaloCronograma)

cronograma_planificado.connect(asignar_costo_cronograma,
        sender=Cronograma)
