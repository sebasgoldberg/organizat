/**
 * Obtención del color de los intervalos.
 */

if (!planificacion)
    var planificacion = {};

(function($){

    function get_color_range(value){
        return (value*24)%192;
    }

    function get_rgb_color(r,g,b,cuello_botella, transparencia){
        if (cuello_botella)
            return 'rgba(255,0,0,'+transparencia+')';
        return 'rgba('+get_color_range(r)+','+get_color_range(g)+','+get_color_range(b)+','+transparencia+')';
    }

    function Cronograma(id, admin_url){
        this.id = id;
        this.admin_url = admin_url;

        this.mostrar = function(){
            window.open(this.admin_url, '_blank'); 
        }
    }

    function Intervalo(id, cronograma, pedido, item, producto, maquina, tarea, cantidad, fechaDesde, fechaHasta, estado, urlCancelar, urlFinalizar, scheduler){
        this.id = id;
        this.cronograma = cronograma;
        this.pedido = pedido;
        this.item = item;
        this.producto = producto;
        this.maquina = maquina;
        this.tarea = tarea;
        this.cantidad = cantidad;
        this.fechaDesde = fechaDesde;
        this.fechaHasta = fechaHasta;
        this.estado = estado;
        this.urlCancelar = urlCancelar;
        this.urlFinalizar = urlFinalizar;
        this.scheduler = scheduler;

        this.getColor = function(){
            var transparencia = '1';
            if ( this.estado=='Planificado' )
                transparencia = '0.5';
            else if ( this.estado=='Cancelado' )
                transparencia = '0.25';
            
            return get_rgb_color(128,this.tarea.id,this.item.id,false,transparencia);
        };

        this.getDescripcion = function(){
            return '#'+this.pedido.id+'#'+
                this.item.id+':'+
                this.tarea.descripcion+'('+
                this.producto.descripcion+'):'+
                this.cantidad.toString()+' ['+
                this.estado+']';
        };

        this.quick_info_content = function(){
            thisIntervalo = this;
            $qic = $('#quick-info-content');
            $qic.find('li').each(function(){
                $this = $(this);
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

        this.updateFromData = function(data){
            this.scheduler.updateEventFromIntervaloData(intervalo);
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
                    for (var i=0; i<respuesta.intervalos_finalizados.length; i++){
                        intervalo = respuesta.intervalos_finalizados[i];
                        thisIntervalo.updateFromData(intervalo);
                    }
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
                    var intervalosCancelados = respuesta.intervalos_cancelados;
                    for(i=0; i<intervalosCancelados.length; i++){
                        intervalo = intervalosCancelados[i];
                        thisIntervalo.updateFromData(intervalo);
                        //thisIntervalo.scheduler.deleteEvent(event_id);
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

        this.verCronograma = function(){
            this.cronograma.mostrar();
        }

    }


    planificacion.Intervalo = Intervalo;
    planificacion.Cronograma = Cronograma;


})(jQuery);

