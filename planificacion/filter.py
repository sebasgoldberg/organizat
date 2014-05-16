from django.contrib import admin
from django.utils.translation import ugettext as _

class CuelloBotellaListFilter(admin.SimpleListFilter):

  title = _('Es cuello de botella')

  parameter_name = 'es_cuello_botella'

  def lookups(self, request, model_admin):
    return (
      ('1',_(u'Verdadero')),
      ('0',_(u'Falso')),
      )

  def queryset(self, request, queryset):

    if self.value():
      intervalos_cuellos_botella = []
      for intervalo in queryset.all():
        if intervalo.in_maquina_cuello_botella():
          intervalos_cuellos_botella.append(intervalo.id)
      es_cuello_botella = self.value()
      if es_cuello_botella == '1':
        return queryset.filter(id__in=intervalos_cuellos_botella)
      else:
        return queryset.exclude(id__in=intervalos_cuellos_botella)
    return queryset


