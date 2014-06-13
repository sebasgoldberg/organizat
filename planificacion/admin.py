from django.contrib import admin
from planificacion.models import *
from planificacion.filter import CuelloBotellaListFilter

class PedidoCronogramaInline(admin.TabularInline):
  model=PedidoCronograma
  extra = 1

class MaquinaCronogramaInline(admin.TabularInline):
  model=MaquinaCronograma
  extra = 1

class CronogramaAdmin(admin.ModelAdmin):
  readonly_fields=['id','estado']
  inlines=[PedidoCronogramaInline,MaquinaCronogramaInline]
  list_display=['id','descripcion', 'fecha_inicio', 'estrategia']
  list_display_links = ('id', 'descripcion')
  search_fields=['descripcion']
  list_per_page = 40

class IntervaloCronogramaAdmin(admin.ModelAdmin):
  list_display=['id', 'maquina', 'tarea', 'pedido', 'producto', 'cantidad_tarea', 'tiempo_intervalo', 
    'in_maquina_cuello_botella', 'fecha_desde', 'fecha_hasta']
  list_display_links = ('id',)
  list_filter=['cronograma', 'maquina', 'tarea', 'pedido', 'producto', CuelloBotellaListFilter]
  list_per_page = 40
  date_hierarchy='fecha_desde'

admin.site.register(Cronograma,CronogramaAdmin)
admin.site.register(IntervaloCronograma,IntervaloCronogramaAdmin)
