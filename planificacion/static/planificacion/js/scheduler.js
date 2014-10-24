if (!planificacion)
    var planificacion = {};

(function($){


    function crearScheduler(scheduler, maquinas, fechaInicio, intervalos) {

        scheduler.locale.labels.timeline_tab = gettext("Línea Tmp");
        scheduler.locale.labels.unit_tab = gettext("Calendario");
        scheduler.locale.labels.section_custom="Section";
        scheduler.config.xml_date="%Y-%m-%d %H:%i";
        scheduler.config.readonly=true;
        scheduler.config.readonly_form=true;
        scheduler.itemIdSelected = null;

        //block all modifications
        scheduler.attachEvent("onBeforeDrag",function(){return false;})

        // -------------------------------------------------------
        // Quick info
        // -------------------------------------------------------
        scheduler.templates.quick_info_content = function(start, end, ev){ 
            return ev.intervalo.quick_info_content()
        };
        scheduler.config.quick_info_detached = true;
        scheduler.config.icons_select = ['icon_ic_finalizar',
            'icon_ic_cancelar',
            'icon_ic_ver_cronograma', ];

        /**
         * Botón "Finalizar"
         */
        scheduler.locale.labels.icon_ic_finalizar = gettext("Finalizar");
        scheduler._click.buttons.ic_finalizar = function(id){
            schEvent = scheduler.getEvent(id);
            schEvent.intervalo.finalizar();
        };

        /**
         * Botón "Cancelar"
         */
        scheduler.locale.labels.icon_ic_cancelar = gettext("Cancelar");
        scheduler._click.buttons.ic_cancelar = function(id){
            schEvent = scheduler.getEvent(id);
            schEvent.intervalo.cancelar();
        };

        /**
         * Botón "Ver cronograma"
         */
        scheduler.locale.labels.icon_ic_ver_cronograma = gettext("Ver cronograma");
        scheduler._click.buttons.ic_ver_cronograma = function(id){
            schEvent = scheduler.getEvent(id);
            schEvent.intervalo.verCronograma();
        };


        scheduler.initializeEventIntervaloMap = function(){
            this.eventIdFromIntervaloId = {};
            var events = this.getEvents();
            for (i=0; i<events.length; i++){
                var _event = events[i];
                this.eventIdFromIntervaloId[_event.intervalo.id] = _event.id;
            }
        };

        scheduler.getEventIdFromIntervaloId = function(intervaloId){
            return this.eventIdFromIntervaloId[intervaloId];
        };

        scheduler.updateEventFromIntervaloData = function(intervaloData){
            event_id = this.getEventIdFromIntervaloId(intervalo.id);
            _event = this.getEvent(event_id);
            _event.intervalo.estado = intervalo.estado;
            _event.text = _event.intervalo.getDescripcion();
            _event.color = _event.intervalo.getColor();
            this.updateEvent(event_id);
        }

        scheduler.templates.event_class = function(start, end, ev){
            return 'item_'+ev.intervalo.item.id;
        }

        scheduler.refreshItemSelected = function(){
            if (this.itemIdSelected)
                $('.item_'+this.itemIdSelected).addClass('item_selected');
        }

        scheduler.setEventsAsSelectedByEventItem = function(eventId){
            _event = this.getEvent(eventId);
            if (_event.intervalo.item.id == this.itemIdSelected)
                return
            $('.item_'+this.itemIdSelected).removeClass('item_selected');
            this.itemIdSelected = _event.intervalo.item.id;
            this.refreshItemSelected();
        }

        scheduler.attachEvent("onClick",function(id, e){
            this.setEventsAsSelectedByEventItem(id);
            return false;
            });

        scheduler.showMiniCal = function(){
            if (this.isCalendarVisible()){
                this.destroyCalendar();
            } else {
                this.renderCalendar({
                    position:"dhx_minical_icon",
                    date:scheduler._date,
                    navigation:true,
                    handler:function(date,calendar){
                        this.setCurrentView(date);
                        this.destroyCalendar()
                    }
                });
            }
        }

        scheduler.registerMinical = function(){
            thisScheduler = this;
            $('#dhx_minical_icon').click(function(){
                thisScheduler.showMiniCal();
            })
        };

        scheduler.registerMinical();

        scheduler.attachEvent("onViewChange", function (new_mode , new_date){
            this.refreshItemSelected();
        });

        scheduler.attachEvent("onDblClick",function(id, e){
          return false;
          });

        scheduler.config.details_on_dblclick = false;
        scheduler.config.dblclick_create = false;
        scheduler.config.first_hour = 6
        scheduler.config.last_hour = 23

        //===============
        //Configuration
        //===============
        var sections=[];
        for (i=0; i<maquinas.length; i++){
            maquina = maquinas[i]
            sections.push({key:maquina.id, label:maquina.descripcion});
        }

        scheduler.createTimelineView({
            name:	"timeline",
            x_unit:	"minute",
            x_date:	"%H:%i",
            x_step:	60,
            x_size: 12,
            x_start: 8,
            x_length:	24,
            y_unit:	sections,
            y_property:	"section_id",
            render:"bar"
        });

        scheduler.createUnitsView("unit","section_id",sections);
            
        //===============
        //Data loading
        //===============
        scheduler.config.lightbox.sections=[	
            {name:"description", height:130, map_to:"text", type:"textarea" , focus:true},
            {name:"custom", height:23, type:"select", options:sections, map_to:"section_id" },
            {name:"time", height:72, type:"time", map_to:"auto"}
        ]

        events = [];
        for (i=0; i<intervalos.length; i++){
            intervalo = intervalos[i];
            events.push({
                intervalo: intervalo,
                start_date: intervalo.fechaDesde,
                end_date: intervalo.fechaHasta,
                text:intervalo.getDescripcion(),
                section_id:intervalo.maquina.id,
                color: intervalo.getColor(),
            });
        }

        scheduler.parse(events,"json");

        scheduler.initializeEventIntervaloMap();
    }

    const CELL = {
        PEDIDOS: 'a',
        ITEMS: 'b',
        ESTADO: 'c',
        TIMELINE: 'd',
    };

    GridPedidos = function(pedidos, grid){

        this.init = function(pedidos, grid){
            this.grid = grid;
            this.pedidos = pedidos;
            this.grid.setImagePath("./codebase/imgs/"); // TODO Verificar si está OK el path
            this.grid.setHeader(
                    gettext('ID')+','+
                    gettext('Descripcion')+','+
                    gettext('Estado')+','+
                    gettext('% Planificado')+','+
                    gettext('% Finalizado'));
            this.grid.setInitWidths("50,150,100,100,100");
            this.grid.setColAlign("right,left,left,right,right");
            this.grid.setColTypes("ro,ro,ro,ro,ro");
            this.grid.setColSorting("int,str,str,float,float");
            this.grid.init();
            for (var i=0; i<pedidos.length; i++)
                pedido = pedidos[i]
                this.grid.addRow(pedido.id,
                        this.pedidoToLine(pedido));
        };

        this.pedidoToLine = function(pedido){
            return [
                    pedido.id,
                    pedido.descripcion,
                    pedido.estado,
                    pedido.porcentaje_planificado,
                    pedido.porcentaje_finalizado,
                    ];
        };

        this.init(pedidos, grid);
    };

    TimeLineConsole = function(scheduler, maquinas, fechaInicio, intervalos, pedidos, container){

        thisTimeLineConsole = this;

        this.scheduler = scheduler;
        this.layout = new dhtmlXLayoutObject({
            parent: container,
            pattern: "4U",
            cells: [
                {id: CELL.PEDIDOS, text: gettext('Pedido')},
                {id: CELL.ITEMS, text: gettext('Items Pedido')},
                {id: CELL.ESTADO, text: gettext('Estado de Avance Item')},
                {id: CELL.TIMELINE, text: gettext('Línea de Tiempo'), height: 500}]
            });

        this.createGridPedidos = function(pedidos){

            this.gridPedidos = new GridPedidos(pedidos,
                    this.layout.cells(CELL.PEDIDOS).attachGrid());

        };


        crearScheduler(this.scheduler, maquinas, fechaInicio, intervalos);

        this.updateResize = function(pannelsIds){
            for (var i=0; i<pannelsIds.length; i++){
                if (pannelsIds[i] === CELL.TIMELINE){
                    this.scheduler.refreshItemSelected();
                    return;
                }
            }
        }

        this.layout.attachEvent("onPanelResizeFinish", function(ids){
            thisTimeLineConsole.updateResize(ids)
        });

        this.layout.attachEvent("onExpand", function(id){
            thisTimeLineConsole.updateResize([id])
            });

        this.layout.cells(CELL.TIMELINE).attachScheduler(fechaInicio, "timeline", 'scheduler_here');

        this.createGridPedidos(pedidos);

    }



    planificacion.TimeLineConsole = TimeLineConsole;

})(jQuery);
