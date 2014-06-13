from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('planificacion.views',
    # Examples:
    # url(r'^$', 'alternativa.views.home', name='home'),
    # url(r'^alternativa/', include('alternativa.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^planificar/(\d+)/$', 'planificar'),
    url(r'^invalidar/(\d+)/$', 'invalidar'),
    url(r'^activar/(\d+)/$', 'activar'),
    url(r'^desactivar/(\d+)/$', 'desactivar'),
    url(r'^calendario/cronograma/(\d+)/$', 'calendario_cronograma'),
)

