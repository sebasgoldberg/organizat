# coding=utf-8
from django.shortcuts import render, redirect
from .models import Cronograma, IntervaloCronograma
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.views.generic import View
from datetime import datetime as DT
from produccion.models import Maquina
import datetime
from django.db.models import Min
from datetime import timedelta as TD

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


def vista_timeline(request, intervalos, fecha_inicio=None):

    if fecha_inicio is None:
      fecha_inicio = intervalos.aggregate(Min('fecha_desde'))['fecha_desde__min']

    if fecha_inicio is None:
      fecha_inicio = DT.now()

    maquinas = set()
    for i in intervalos:
        if i.maquina not in maquinas:
            maquinas.add(i.maquina)

    return render(request,
#'planificacion/cronograma/calendario.html',
#'planificacion/cronograma/scheduler.html',
    'planificacion/cronograma/timeline.html',
    {'fecha_inicio': fecha_inicio,
    'intervalos': intervalos,
    'maquinas': maquinas})

def calendario_cronograma(request, id_cronograma):
  cronograma = Cronograma.objects.get(id=id_cronograma)
  intervalos = IntervaloCronograma.get_intervalos_no_cancelados(
      ).filter(cronograma=cronograma)
  fecha_inicio = cronograma.fecha_inicio
  return vista_timeline(request, intervalos)

def calendario_activo(request):
    intervalos = IntervaloCronograma.get_intervalos_activos(
            ).filter(fecha_desde__gte=datetime.date.today())
    return vista_timeline(request, intervalos)

def calendario(request):
    intervalos = IntervaloCronograma.objects.filter(
            fecha_desde__gte=datetime.date.today()-TD(days=7))
    return vista_timeline(request, intervalos)


from django.http import HttpResponse
import json

def rest_cancelar_intervalo(request, pk):
    intervalo = IntervaloCronograma.objects.get(pk=pk)
    try:
        intervalos_cancelados = intervalo.cancelar()
        ids_intervalos_cancelados = [ x.id for x in intervalos_cancelados]

        return HttpResponse(json.dumps({
            'ids_intervalos_cancelados': ids_intervalos_cancelados,
            'mensajes': [ _(u'Se ha(n) cancelado %s intervalo(s) en forma exitosa.'
                ) % len(intervalos_cancelados), ],
            }))
    except Exception as e:
        errores = [
                _(u'Ha ocurrido un error al intentar cancelar el intervalo %s.') % intervalo,
                e.message, ]
        return HttpResponse(
                json.dumps({'mensajes': errores}),
                status=400)

def rest_finalizar_intervalo(request, pk):
    intervalo = IntervaloCronograma.objects.get(pk=pk)
    try:
        intervalo.finalizar()

        intervalos_finalizados = [ {
            'id': intervalo.id,
            'estado': intervalo.get_descripcion_estado() }, ]

        return HttpResponse(json.dumps({
            'intervalos_finalizados': intervalos_finalizados,
            'mensajes': [ _(u'Se ha(n) finalizado %s intervalo(s) en forma exitosa.'
                ) % len(intervalos_finalizados), ],
            }))
    except Exception as e:
        errores = [
                _(u'Ha ocurrido un error al intentar finalizar el intervalo %s.') % intervalo,
                e.message, ]
        return HttpResponse(
                json.dumps({'mensajes': errores}),
                status=400)

