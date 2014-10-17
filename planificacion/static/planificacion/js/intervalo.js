/**
 * Obtención del color de los intervalos.
 */

var planificacion = {};

(function($){

    function get_color_range(value){
        return (value*24)%192;
    }

    function get_rgb_color(r,g,b,cuello_botella){
        if (cuello_botella)
            return 'rgb(255,0,0)';
        return 'rgb('+get_color_range(r)+','+get_color_range(g)+','+get_color_range(b)+')'
    }

    function Intervalo(id, pedido, item, producto, maquina, tarea, cantidad, fechaDesde, fechaHasta, urlCancelar, urlFinalizar, scheduler){
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
        this.urlFinalizar = urlFinalizar;
        this.scheduler = scheduler;

        this.getColor = function(){
            return get_rgb_color(128,this.tarea.id,this.item.id,false);
        };

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

        this.finalizar = function(){
            var thisIntervalo = this;
            message.check_continue(
                    gettext('¿Está seguro que desea finalizar el intervalo?'),
                    function(){
                        thisIntervalo.doFinalizar();
                    });
        }

        this.doFinalizar = function(){
            thisIntervalo = this;
            message.info([gettext("Finalizando intervalo...")]);
            console.log(thisIntervalo.urlFinalizar)
            $.get(
                thisIntervalo.urlFinalizar,
                function(data){
                    var respuesta = $.parseJSON(data);
                    message.info(respuesta.mensajes);
                }
            ).fail(
                function(data){
                    if (!data.responseText){
                        message.error([gettext('Ha ocurrido un error al intentar realizar la operación')]);
                        return;
                    }
                    var errores = $.parseJSON(data.responseText).mensajes;
                    message.error(errores);
                }
            );
        }

        this.cancelar = function(){
            var thisIntervalo = this;
            message.check_continue(
                    gettext('¿Está seguro que desea cancelar el intervalo seleccionado y todos los intervalos dependientes?'),
                    function(){
                        thisIntervalo.doCancelar();
                    });
        }

        this.doCancelar = function(){
            thisIntervalo = this;
            message.info([gettext("Cancelando intervalos...")]);
            $.get(
                thisIntervalo.urlCancelar,
                function(data){
                    var respuesta = $.parseJSON(data);
                    var idsIntervalosCancelados = respuesta.ids_intervalos_cancelados;
                    for(i=0; i<idsIntervalosCancelados.length; i++){
                        event_id = thisIntervalo.scheduler.getEventIdFromIntervaloId(idsIntervalosCancelados[i]);
                        thisIntervalo.scheduler.deleteEvent(event_id);
                    }
                    message.info(respuesta.mensajes);
                }
            ).fail(
                function(data){
                    if (!data.responseText){
                        message.error([gettext('Ha ocurrido un error al intentar realizar la operación')]);
                        return;
                    }
                    var errores = $.parseJSON(data.responseText).mensajes;
                    message.error(errores);
                }
            );
        }

    }

    planificacion.Intervalo = Intervalo;

})(jQuery);

