# coding=utf-8
from django.shortcuts import render, redirect
from .models import Cronograma, IntervaloCronograma
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.views.generic import View
from datetime import datetime as DT

class ExecuteMethodView(View):
  _class = None
  method = None

  def get(self, request, *args, **kwargs):
    instance = self._class.objects.get(pk=self.kwargs['pk'])
    try:
      self.method(instance)
      messages.success(request, _(u'Operación realizada en forma exitosa.'))
    except ValidationError as e:
      messages.error(request, e)
    return self.redirect(instance)
  
  def redirect(self, instance):
    raise Exception(_(u'Método no implementado.'))

class ExecuteCronogramaMethodView(ExecuteMethodView):
  _class = Cronograma

  def redirect(self, instance):
    return redirect('/admin/planificacion/cronograma/%s/' % instance.id)

class ExecuteIntervaloCronogramaMethodView(ExecuteMethodView):
  _class = IntervaloCronograma

  def redirect(self, instance):
    return redirect('/admin/planificacion/intervalocronograma/%s/' % instance.id)

def calendario_cronograma(request, id_cronograma):
  cronograma = Cronograma.objects.get(id=id_cronograma)
  intervalos = cronograma.intervalocronograma_set.all()
  fecha_inicio = cronograma.fecha_inicio
  return render(request,
    'planificacion/cronograma/calendario.html',
    {'fecha_inicio': fecha_inicio,
    'intervalos': intervalos,})

def calendario_activo(request):
  intervalos = IntervaloCronograma.get_intervalos_activos()
  fecha_inicio = DT.now()
  return render(request,
    'planificacion/cronograma/calendario.html',
    {'fecha_inicio': fecha_inicio,
    'intervalos': intervalos,})
