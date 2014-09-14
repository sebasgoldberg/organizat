from django.contrib import admin
from costos.models import *

class CostoMaquinaAdmin(admin.ModelAdmin):
  list_display = ['id', 'maquina', 'costo_por_hora',]
  list_display_links = ('id',)
  #list_filter = ['maquina',]
  list_editable = ['costo_por_hora', ]
  list_per_page = 40
  search_fields = ['maquina__descripcion']

class CostoCronogramaAdmin(admin.ModelAdmin):
  list_display = ['id', 'cronograma', 'costo',]
  list_display_links = ('id',)
  list_per_page = 40
  search_fields = ['descripcion__descripcion']


admin.site.register(CostoMaquina, CostoMaquinaAdmin)
admin.site.register(CostoCronograma, CostoCronogramaAdmin)
