from django.contrib import admin
from planificacion.models import *

class PedidoCronogramaInline(admin.TabularInline):
  model=PedidoCronograma
  extra = 1

class MaquinaCronogramaInline(admin.TabularInline):
  model=MaquinaCronograma
  extra = 1

class CronogramaAdmin(admin.ModelAdmin):
  inlines=[PedidoCronogramaInline,MaquinaCronogramaInline]
  list_display=['id','descripcion', 'intervalo_tiempo', 'fecha_inicio', 'estrategia']
  list_display_links = ('id', 'descripcion')
  search_fields=['descripcion']
  list_per_page = 40

class IntervaloCronogramaAdmin(admin.ModelAdmin):
  list_display=['cronograma', 'maquina', 'secuencia', 'tarea', 'pedido', 'producto', 'cantidad_tarea', 'cantidad_producto', 'tiempo_intervalo']
  list_display_links = ('cronograma', 'maquina', 'secuencia')
  list_filter=['cronograma', 'maquina', 'tarea', 'pedido', 'producto']
  list_per_page = 40

admin.site.register(Cronograma,CronogramaAdmin)
admin.site.register(IntervaloCronograma,IntervaloCronogramaAdmin)
