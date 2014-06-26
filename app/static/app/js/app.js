var SEGUNDOS_X_PIXEL = 84400 / 1024;

function segundosAPixels(segundos){
  return Math.floor( segundos / SEGUNDOS_X_PIXEL );
  }

function Param(){
	
	this.setFechaPlanificacion = function(fecha){
		this.fechaPlanificacion = fecha;
	}
	
	this.getFechaPlanificacion = function(){
		return this.fechaPlanificacion;
	}

}

Param.instance = null;

Param.getInstance = function(){
	if (Param.instance === null)
		Param.instance = new Param();
	return Param.instance;
};

/*
 * Definición de las distintas longitudes de un intervalo.
 * Como representamos 24 hs de 1 día, y cada hora la 
 * dividimos en 4, entonces tendremos 96 longitudes posibles.
 * Respecto de las posiciones posibles, las mismas iran
 * desde 0 hasta 95.
 */
function Intervalo(intervalo){
	
	this.id = intervalo.id;
	this.fecha_desde = new Date(intervalo.fecha_desde);
	this.fecha_hasta = new Date(intervalo.fecha_hasta);

  this.getDuracionEnSegundos = function(){
    return moment.duration(this.fecha_hasta - this.fecha_desde).asSeconds();
    }

  this.getWidth = function(){
    /*
     * Obtiene el ancho en función del intervalo
     * de tiempo del intervalo
     */
    var segundos = this.getDuracionEnSegundos();
    var pixels = segundosAPixels(segundos);
    return pixels+'px';
    };

  this.getInicioEnSegundos = function(){
    return moment.duration(this.fecha_desde - 
    	Param.getInstance().getFechaPlanificacion()).asSeconds();
    };

  this.getLeftPosition = function(){
    /*
     * Obtiene la posición en función de la fecha de
     * inicio del intervalo
     */
    var segundos_inicio = this.getInicioEnSegundos();
    var pixels = segundosAPixels(segundos_inicio);
    return pixels+'px';
    };

	this.setMaquina = function(maquina){
		this.maquina = maquina;
	}
	
  }

function Maquina(maquina, intervalos){

	this.id = maquina.id;
	this.descripcion = maquina.descripcion;
	this.intervalos = [];
	
	this.addIntervalo = function(intervalo){
		intervalo.setMaquina(this);
		this.intervalos.push(intervalo);
	}

	for(var i=0;i<intervalos.length;i++){
		var intervalo = new Intervalo(intervalos[i]);
		this.addIntervalo(intervalo);		
	}

}

(function(){
  var app = angular.module('djprod', [ ]);

  app.directive('datepicker', function() {
    return {
      restrict: 'A',
      require : 'ngModel',
      link : function (scope, element, attrs, ngModelCtrl) {
        $(function(){
          element.datepicker({
            dateFormat:'dd/mm/yy',
            changeMonth: true,
            changeYear: true,
            onSelect:function (date) {
              scope.$apply(function () {
                ngModelCtrl.$setViewValue(date);
              });
            }
          });
        });
      }
    }
  });

  //---------------------------------------------
  // Planificacion Diaria
  //---------------------------------------------
  app.directive('planificacionDiaria',function(){
    return {
      restrict: 'E',
      templateUrl: 'planificacionDiaria.html',
      controller: function($rootScope, $scope, $http){

        $scope.fechaPlanificacion = '19/05/2014';

		this.selectMaquinas = function(fecha){
            $scope.maquinas = [];
			var mfecha = moment(fecha,'DD-MM-YYYY');
            Param.getInstance().setFechaPlanificacion(mfecha);
            var response = $http.get(
            	"/app/rest/maquinas/y/intervalos/"+
            	mfecha.format('YYYY')+"/"+
            	mfecha.format('MM')+"/"+
            	mfecha.format('DD')+"/"+
            	".json");

            response.success(function(data, status, headers, config) {
            	$scope.maquinas = [];
            	for (var i=0; i < data.length; i++){
            		var maquina = new Maquina(data[i].maquina, data[i].intervalos)
            		$scope.maquinas.push(maquina);
            	}
          		$rootScope.$broadcast('fechaPlanificacionModificada',$scope.maquinas)
            });
            response.error(function(data, status, headers, config) {
            	$scope.maquinas = [];
                alert("AJAX failed!");
          		$rootScope.$broadcast('fechaPlanificacionModificada',$scope.maquinas)
             });
		};

        this.selectPlanificacionDiaria = function(){
          $scope.maquinas = [ ];
          this.selectMaquinas($scope.fechaPlanificacion);          
          };

        this.fechaPlanificacionModificada = function(fecha){
          this.selectPlanificacionDiaria(fecha);
          };

        this.selectPlanificacionDiaria();

        },
      controllerAs: 'planificacionDiariaCtrl'
      };
    });

  //---------------------------------------------
  // Detalle de intervalos seleccionados
  //---------------------------------------------
  app.directive('detalleIntervalosSeleccionados',function(){
    return {
      restrict: 'E',
      templateUrl: 'intervalo/detalle.html',
      controller: function($scope){
        $scope.intervalos = [];
        $scope.$on('fechaPlanificacionModificada',function(event, maquinas){
          $scope.intervalos = [];
          });
        
        this.addIntervaloSeleccionado = function(intervalo){
          var index = $scope.intervalos.indexOf(intervalo);
          if (index == 0)
            return;
          if (index >= 0)
            $scope.intervalos.splice(index, 1);
          $scope.intervalos.unshift(intervalo);
          };

        },
      controllerAs: 'detalleIntervalosSeleccionadosCtrl'
      };
    });

  //---------------------------------------------
  // Detalle maquina seleccionada
  //---------------------------------------------
  app.directive('detalleMaquinaSeleccionada',function(){
    return {
      restrict: 'E',
      templateUrl: 'maquina/detalle.html',
      controller: function($scope){
        $scope.maquina = null;
        $scope.$on('fechaPlanificacionModificada',function(event, maquinas){
          $scope.maquina = null;
          });
        
        this.setMaquina = function(maquina){
          if ($scope.maquina == maquina)
            return;
          $scope.maquina = maquina;
          };

        },
      controllerAs: 'detalleMaquinaSeleccionadaCtrl'
      };
    });


})();
