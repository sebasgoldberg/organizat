from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.views.generic.base import TemplateView
from .views import AppView

from .rest.views import MaquinasYIntervalos

from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.auth.decorators import login_required

urlpatterns = format_suffix_patterns(patterns('',
    url(r'^rest/maquinas/y/intervalos/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', MaquinasYIntervalos.as_view()),
)) + patterns('',
    url(r'^(?P<path>.*)$', login_required( AppView.as_view() ) ),
)
