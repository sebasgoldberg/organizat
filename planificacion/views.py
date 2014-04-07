from django.shortcuts import render, redirect
from planificacion.models import Cronograma

def planificar(request,id_cronograma):
  cronograma = Cronograma.objects.get(id=id_cronograma)
  cronograma.planificar()
  return redirect('/admin/planificacion/intervalocronograma/?cronograma__id__exact=%s' % id_cronograma)
