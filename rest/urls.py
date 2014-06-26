from django.conf.urls import patterns, include, url
from rest_framework import viewsets, routers
from planificacion.models import (IntervaloCronograma, Cronograma, 
                                  MaquinaPlanificacion, Tarea, Producto,
                                  PedidoPlanificable, TareaMaquina,
                                  TareaProducto, ItemPlanificable,
                                  PedidoCronograma, MaquinaCronograma)

def addClassToRouter(router, _class):
    viewSetClass = type('%sViewSet' % _class.__name__,
                        (viewsets.ModelViewSet,),
                        {'model':_class,})
    router.register(r'%s' % _class.__name__, viewSetClass)

router = routers.DefaultRouter()
for _class in [IntervaloCronograma,
               Cronograma,
               MaquinaPlanificacion,
               Tarea,
               Producto,
               PedidoPlanificable,
               TareaMaquina,
               TareaProducto,
               ItemPlanificable,
               PedidoCronograma,
               MaquinaCronograma]:
    addClassToRouter(router, _class)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)