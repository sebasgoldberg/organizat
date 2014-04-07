from django.contrib import admin
from produccion.models import *



class DependenciaTareaProductoInline(admin.TabularInline):
  model=DependenciaTareaProducto
  extra = 1

class TareaMaquinaInline(admin.TabularInline):
  model=TareaMaquina
  extra = 1

class TareaProductoInline(admin.TabularInline):
  model=TareaProducto
  extra = 1

class MaquinaAdmin(admin.ModelAdmin):
  inlines=[TareaMaquinaInline]
  list_display=['id','descripcion']
  list_display_links = ('id', 'descripcion')
  search_fields=['descripcion']
  list_per_page = 40

class TareaAdmin(admin.ModelAdmin):
  inlines=[TareaMaquinaInline,TareaProductoInline]
  list_display=['id','descripcion','tiempo']
  list_display_links = ('id', 'descripcion')
  search_fields=['descripcion']
  list_per_page = 40

class ProductoAdmin(admin.ModelAdmin):
  inlines=[TareaProductoInline]
  list_display=['id','descripcion']
  list_display_links = ('id', 'descripcion')
  search_fields=['descripcion']
  list_per_page = 40

class ProductoProxyDependenciasTareasAdmin(admin.ModelAdmin):
  inlines=[DependenciaTareaProductoInline]
  list_display=['id','descripcion']
  list_display_links = ('id', 'descripcion')
  search_fields=['descripcion']
  list_per_page = 40

class TiempoRealizacionTareaAdmin(admin.ModelAdmin):
  list_display=['id','maquina', 'producto', 'tarea', 'tiempo', 'activa']
  list_display_links = ('id', )
  list_filter=['maquina', 'producto', 'tarea']
  list_editable=['tiempo', 'activa']
  list_per_page = 40

class ItemPedidoInline(admin.TabularInline):
  model=ItemPedido
  extra = 1

class PedidoAdmin(admin.ModelAdmin):
  inlines=[ItemPedidoInline]
  list_display=['id','descripcion', 'fecha_entrega']
  list_display_links = ('id', 'descripcion')
  search_fields=['descripcion']
  list_per_page = 40

admin.site.register(Maquina,MaquinaAdmin)
admin.site.register(Tarea,TareaAdmin)
admin.site.register(Producto,ProductoAdmin)
admin.site.register(ProductoProxyDependenciasTareas,ProductoProxyDependenciasTareasAdmin)
admin.site.register(TiempoRealizacionTarea,TiempoRealizacionTareaAdmin)
admin.site.register(Pedido,PedidoAdmin)
