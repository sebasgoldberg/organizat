var SEGUNDOS_X_PIXEL = 84400 / 1024;

function segundosAPixels(segundos){
  return Math.floor( segundos / SEGUNDOS_X_PIXEL );
  }

/*
 * Definición de las distintas longitudes de un intervalo.
 * Como representamos 24 hs de 1 día, y cada hora la 
 * dividimos en 4, entonces tendremos 96 longitudes posibles.
 * Respecto de las posiciones posibles, las mismas iran
 * desde 0 hasta 95.
 */
function crearIntervalo(intervalo){

  intervalo.getDuracionEnSegundos = function(){
    return moment.duration(this.fecha_hasta - this.fecha_desde).asSeconds();
    }

  intervalo.getWidth = function(){
    /*
     * Obtiene el ancho en función del intervalo
     * de tiempo del intervalo
     */
    segundos = this.getDuracionEnSegundos();
    pixels = segundosAPixels(segundos);
    return pixels+'px';
    };

  intervalo.getInicioEnSegundos = function(fechaPlanificacion){
    return moment.duration(this.fecha_desde - fechaPlanificacion).asSeconds();
    };

  intervalo.getLeftPosition = function(fechaPlanificacion){
    /*
     * Obtiene la posición en función de la fecha de
     * inicio del intervalo
     */
    segundos_inicio = this.getInicioEnSegundos(fechaPlanificacion);
    pixels = segundosAPixels(segundos_inicio);
    return pixels+'px';
    };

  return intervalo;

  }

(function(){
  var app = angular.module('djprod', [ ]);

  var intervalos = [
    {
      id: 100,
      fecha_desde: new Date(2014,6,23,10),
      fecha_hasta: new Date(2014,6,23,10,30)
      },
    {
      id: 101,
      fecha_desde: new Date(2014,6,23,16),
      fecha_hasta: new Date(2014,6,23,18)
      },
  ];

  for(i=0;i<intervalos.length;i++){
    intervalos[i]=crearIntervalo(intervalos[i]);
    }

  var maquinas = [
    {
      id: 10,
      descripcion: 'Malaxador',
      intervalos: intervalos
      },
    {
      id: 11,
      descripcion: 'Compresor',
      intervalos: intervalos
      },
  ];

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
      controller: function($rootScope, $scope){

        $scope.fechaPlanificacion = new Date(2014,6,23);

        this.selectPlanificacionDiaria = function(){
          $scope.maquinas = [ ];
          $scope.maquinas = maquinas;
          };

        this.fechaPlanificacionModificada = function(fecha){
          this.selectPlanificacionDiaria();
          $rootScope.$broadcast('fechaPlanificacionModificada',$scope.maquinas)
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
