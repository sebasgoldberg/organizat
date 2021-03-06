from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from .views import ExecuteCronogramaMethodView, ExecuteIntervaloCronogramaMethodView
from .models import Cronograma, IntervaloCronograma

urlpatterns = patterns('planificacion.views',
    # Examples:
    # url(r'^$', 'alternativa.views.home', name='home'),
    # url(r'^alternativa/', include('alternativa.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^planificar/(?P<pk>\d+)/$', 
      ExecuteCronogramaMethodView.as_view(method=Cronograma.planificar)),
    url(r'^invalidar/(?P<pk>\d+)/$', 
      ExecuteCronogramaMethodView.as_view(method=Cronograma.invalidar)),
    url(r'^activar/(?P<pk>\d+)/$', 
      ExecuteCronogramaMethodView.as_view(method=Cronograma.activar)),
    url(r'^desactivar/(?P<pk>\d+)/$', 
      ExecuteCronogramaMethodView.as_view(method=Cronograma.desactivar)),
    url(r'^finalizar/(?P<pk>\d+)/$', 
      ExecuteCronogramaMethodView.as_view(method=Cronograma.finalizar)),

    url(r'^intervalo/finalizar/(?P<pk>\d+)/$', 
      ExecuteIntervaloCronogramaMethodView.as_view(method=IntervaloCronograma.finalizar)),
    url(r'^intervalo/cancelar/(?P<pk>\d+)/$', 
      ExecuteIntervaloCronogramaMethodView.as_view(method=IntervaloCronograma.cancelar)),

    url(r'^calendario/cronograma/(\d+)/$', 'calendario_cronograma'),
    url(r'^calendario/activo/$', 'calendario_activo'),
    url(r'^calendario/$', 'calendario'),

    url(r'^rest/intervalo/cancelar/(?P<pk>\d+)/$', 'rest_cancelar_intervalo', name='cancelar_intervalo'),
    url(r'^rest/intervalo/finalizar/(?P<pk>\d+)/$', 'rest_finalizar_intervalo', name='planificacion.rest.finalizar_intervalo'),
)

