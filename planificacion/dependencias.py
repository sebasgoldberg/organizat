class DependenciasManager:

  def __init__()
  
  def get_instance():
    if self.instance is None:
      self.instance = DependenciasManager()
    return self.instance

  def get_intervalos_mismo_producto_pedido(self):
    intervalos = [ i for i in IntervaloCronograma.objects.filter(
      cronograma=self.cronograma,
      producto=self.producto,
      pedido=self.pedido) ]
    if self.id is None:
      intervalos.append(self)
    return intervalos

  def validar_dependencias(self, cronograma, producto, pedido, tarea_anterior, tarea, instante_agregado=None, instantes_borrado=None):
    intervalos=self.get_intervalos_mismo_producto_pedido()
    for tarea_anterior in self.tarea.get_anteriores(self.producto):
      particion_temporal = self.get_particion_ordenada_temporal(
        intervalos, [tarea_anterior,self.tarea])
      for t in particion_temporal:
        cantidad_tarea = self.get_cantidad_tarea_hasta(intervalos, self.tarea, t)
        cantidad_tarea_anterior = self.get_cantidad_tarea_hasta(intervalos, tarea_anterior, t)
        if cantidad_tarea > cantidad_tarea_anterior:
            raise ValidationError(
              "La cantidad %s de tarea %s es mayor que la cantidad %s de la tarea %s de la cual depende en el instante %s" %\
              (cantidad_tarea, self.tarea.descripcion, cantidad_tarea_anterior, tarea_anterior.descripcion, t) )

