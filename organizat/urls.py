from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


js_info_dict = {
    'packages': ('planificacion',),
    }

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'organizat.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^planificacion/', include('planificacion.urls')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)
