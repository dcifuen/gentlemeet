gApp.controller('testCtrl', ['$scope', 'EndpointsService', function ($scope, endpointsService) {


    $scope.$on(endpointsService.ENDPOINTS_READY, function () {
        //load tags
        console.log("Endpoints ready...");

        endpointsService.getTest({}, function (response) {
                console.log(response);
        });
    });

}]);