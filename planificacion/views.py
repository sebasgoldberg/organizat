from django.shortcuts import render, redirect
from planificacion.models import Cronograma
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

def planificar(request,id_cronograma):
  cronograma = Cronograma.objects.get(id=id_cronograma)
  try:
    cronograma.planificar()
    messages.success(request, _(u'Cronograma planificado en forma exitosa.'))
  except ValidationError as e:
    messages.error(request, e)
  return redirect('/admin/planificacion/cronograma/%s/' % id_cronograma)

def invalidar(request,id_cronograma):
  cronograma = Cronograma.objects.get(id=id_cronograma)
  try:
    cronograma.invalidar()
    messages.success(request, _(u'Cronograma invalidado en forma exitosa.'))
  except ValidationError as e:
    messages.error(request, e)
  return redirect('/admin/planificacion/cronograma/%s/' % id_cronograma)

def activar(request,id_cronograma):
  cronograma = Cronograma.objects.get(id=id_cronograma)
  try:
    cronograma.activar()
    messages.success(request, _(u'Cronograma activado en forma exitosa.'))
  except ValidationError as e:
    messages.error(request, e)
  return redirect('/admin/planificacion/cronograma/%s/' % id_cronograma)

def desactivar(request,id_cronograma):
  cronograma = Cronograma.objects.get(id=id_cronograma)
  try:
    cronograma.desactivar()
    messages.success(request, _(u'Cronograma desactivado en forma exitosa.'))
  except ValidationError as e:
    messages.error(request, e)
  return redirect('/admin/planificacion/cronograma/%s/' % id_cronograma)

def calendario_cronograma(request, id_cronograma):
  cronograma = Cronograma.objects.get(id=id_cronograma)
  return render(request,
    'planificacion/cronograma/calendario.html',
    {'cronograma': cronograma,})
