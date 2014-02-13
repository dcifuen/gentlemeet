ardx_app.controller('deviceCtrl', ['$scope', '$window', '$http', 'EndpointsService', function ($scope, $window, $http, endpointsService) {
    $scope.device = {};
    $scope.resources = []
    $scope.events = []
    $scope.$on(endpointsService.ENDPOINTS_READY, function () {
        //load tags
        console.log("Endpoints ready...");
        endpointsService.getDevice({'uuid_query': $window.device_uuid}, function (response) {
            if (!response.error) {
                $scope.device = response;
                $scope.listEvents(response.resource_id);
            } else {
                console.error(response);
            }
        });
        endpointsService.listResources({}, function (response) {
            if (!response.error) {
                $scope.resources = response.items;
            } else {
                console.error(response);
            }
        });

    });
    $scope.listEvents = function (resource_id) {
        endpointsService.listEvents({'resource_id': resource_id}, function (response) {
            if (!response.error) {
                $scope.events = response.items;
            } else {
                console.error(response);
            }
        });
    };
    $scope.saveDevice = function () {

        endpointsService.updateDevice($scope.device, function (response) {
            if (!response.error) {
                $scope.device = response;
                $scope.listEvents(response.resource_id);
            } else {
                console.error(response);
            }
        });
    };
}]);
