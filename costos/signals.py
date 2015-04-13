# coding=utf-8
from decimal import Decimal as D
from django.db.models import signals
from produccion.models import Maquina
from costos.models import CostoMaquina, CostoIntervalo, CostoCronograma
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
    try:
        instance.costointervalo
        return
    except CostoIntervalo.DoesNotExist:
        pass
    costomaq = instance.maquina.costomaquina_set.first()
    if costomaq is None:
        return
    costo = (D(instance.get_duracion().total_seconds() / 3600) *
        costomaq.costo_por_hora)
    instance.costointervalo = CostoIntervalo.objects.create(
            costo=costo, intervalo=instance)


def asignar_costo_cronograma(sender, instance, *args, **kwargs):
    try:
        instance.costocronograma
    except CostoCronograma.DoesNotExist:
        instance.costocronograma = CostoCronograma.objects.create(
                cronograma=instance)

    instance.costocronograma.costo = 0
    for i in instance.get_intervalos():
        try:
            instance.costocronograma.costo += i.costointervalo.costo
        except CostoIntervalo.DoesNotExist:
            pass
    instance.costocronograma.clean()
    instance.costocronograma.save()


signals.post_save.connect(crear_maquina_costo)

signals.post_save.connect(crear_costo_intervalo,
        sender=IntervaloCronograma)

cronograma_planificado.connect(asignar_costo_cronograma,
        sender=Cronograma)
