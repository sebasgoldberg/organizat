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

def calendario_cronograma(request, id_cronograma):
  cronograma = Cronograma.objects.get(id=id_cronograma)
  return render(request,
    'planificacion/cronograma/calendario.html',
    {'cronograma': cronograma,})
