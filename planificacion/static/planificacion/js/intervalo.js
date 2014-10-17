/**
 * Obtención del color de los intervalos.
 */

function get_color_range(value){
    return (value*24)%192;
}

function get_rgb_color(r,g,b,cuello_botella){
    if (cuello_botella)
        return 'rgb(255,0,0)';
    return 'rgb('+get_color_range(r)+','+get_color_range(g)+','+get_color_range(b)+')'
}

function Intervalo(id, pedido, item, producto, maquina, tarea, cantidad, fechaDesde, fechaHasta, urlCancelar, scheduler){
    this.id = id;
    this.pedido = pedido;
    this.item = item;
    this.producto = producto;
    this.maquina = maquina;
    this.tarea = tarea;
    this.cantidad = cantidad;
    this.fechaDesde = fechaDesde;
    this.fechaHasta = fechaHasta;
    this.urlCancelar = urlCancelar;
    this.scheduler = scheduler;

    this.getDescripcion = function(){
        return '#'+intervalo.pedido.id+'#'+
            intervalo.item.id+':'+
            intervalo.tarea.descripcion+'('+
            intervalo.producto.descripcion+'):'+
            intervalo.cantidad.toString();
    };

    this.quick_info_content = function(){
        thisIntervalo = this;
        $qic = jQuery('#quick-info-content');
        $qic.find('li').each(function(){
            $this = jQuery(this);
            attr = $this.attr('class');
            $span = $this.find('span');
            if (typeof thisIntervalo[attr] === 'object'){
                $span.html('#'+thisIntervalo[attr].id+' - '+thisIntervalo[attr].descripcion);
            }
            else
                $span.html(thisIntervalo[attr]);
        });
        return $qic.parent().html()
    }

    this.cancelar = function(){
        var thisIntervalo = this;
        (function($){
            dhtmlx.message({
                type:"confirm-warning", 
                text:gettext('¿Está seguro que desea cancelar el intervalo seleccionado y todos los intervalos dependientes?'),
                callback: function(result){
                    if (!result)
                        return;
                    dhtmlx.message({text:gettext("Cancelando intervalos..."), expire: -1});
                    console.log(thisIntervalo.urlCancelar);
                    $.get(
                        thisIntervalo.urlCancelar,
                        function(data){
                            var respuesta = $.parseJSON(data);
                            var idsIntervalosCancelados = respuesta.ids_intervalos_cancelados;
                            for(i=0; i<idsIntervalosCancelados.length; i++){
                                event_id = thisIntervalo.scheduler.getEventIdFromIntervaloId(idsIntervalosCancelados[i]);
                                thisIntervalo.scheduler.deleteEvent(event_id);
                            }
                            for (i=0; i<respuesta.mensajes.length; i++){
                                mensaje = respuesta.mensajes[i];
                                dhtmlx.message({text:mensaje, expire: -1});
                            }
                        }
                    ).fail(
                        function(data){
                            if (!data.responseText){
                                dhtmlx.message({
                                    type:"error",
                                    text:gettext('Ha ocurrido un error al intentar realizar la operación'),
                                    expire: -1});
                                return;
                            }
                            var errores = $.parseJSON(data.responseText).mensajes;
                            for (i=0; i<errores.length; i++){
                                mensaje = errores[i];
                                dhtmlx.message({ type:"error", text:mensaje, expire: -1});
                            }
                        }
                    );

                }
            });
        })(jQuery);
    };
}
