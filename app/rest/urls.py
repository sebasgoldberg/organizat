from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from .views import MaquinasYIntervalos

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'alternativa.views.home', name='home'),
    # url(r'^alternativa/', include('alternativa.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^maquinas/y/intervalos/$', MaquinasYIntervalos.as_view()),
    #url(r'^intervalo/detalle/$', TemplateView.as_view(template_name='app/intervalo/detalle.html')),
)

urlpatterns = format_suffix_patterns(urlpatterns)
