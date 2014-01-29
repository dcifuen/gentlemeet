ardx_app.controller('devicesCtrl', ['$scope', '$window','$http', 'EndpointsService', function($scope, $window, $http,endpointsService) {
    $scope.devices = []
    $scope.$on(endpointsService.ENDPOINTS_READY, function(){
        //load tags
        console.log("Endpoints ready...");
        endpointsService.listDevices({}, function(response){
            if(!response.error){
                $scope.devices = response.items;
            }else{

            }
        });
    });
}]);