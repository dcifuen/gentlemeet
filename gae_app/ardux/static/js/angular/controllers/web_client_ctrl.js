gApp.controller('testCtrl', ['$scope', '$timeout','EndpointsService', function ($scope, $timeout, endpointsService) {
    $scope.getSecondsAsDate = function(seconds){
        return moment().startOf('day').add('s', seconds).toDate();
    };

    $scope.countdownTimer = null;

    $scope.$on(endpointsService.ENDPOINTS_READY, function () {
        //load tags
        console.log("Endpoints ready...");


        endpointsService.getDevice({}, function (response) {
            console.log(response);

            $scope.actual_event = {
                'title':'Event1',
                'time':'02:30 pm',
                'description': 'prueba1',
                'duration':300,
                'attendees':[
                    {'name':'Santiago','attended':true},
                    {'name':'David','attended':true},
                    {'name':'Carlos','attended':true},
                    {'name':'Jorge','attended':false}
                ]
            }

            $scope.countdownTimer  = $timeout($scope.onTimeout, 1000);
        });
    });

    $scope.onTimeout = function(){
        if($scope.actual_event.duration >0){
            $scope.actual_event.duration--;
            $scope.countdownTimer = $timeout($scope.onTimeout, 1000);
        }
    }


    $scope.status = {
        isFirstOpen: true,
        isFirstDisabled: false
    };

    $scope.eventsList = [
        {'title':'Event1', 'time':'02:30 pm', 'description': 'prueba1'},
        {'title':'Event2', 'time':'03:30 pm', 'description': 'prueba2'},
        {'title':'Event2', 'time':'04:30 pm', 'description': 'prueba3'},
    ];

}]);
