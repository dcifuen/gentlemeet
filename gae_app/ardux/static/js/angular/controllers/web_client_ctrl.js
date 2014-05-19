gApp.controller('testCtrl', ['$scope', '$timeout','EndpointsService', function ($scope, $timeout, endpointsService) {
    $scope.getSecondsAsDate = function(seconds){
        return moment().startOf('day').add('s', seconds).toDate();
    };

    $scope.countdownTimer = null;
    $scope.calendarId = 5629499534213120; //Should be device Id

    $scope.$on(endpointsService.ENDPOINTS_READY, function () {
        //load tags
        console.log("Endpoints ready...");


        endpointsService.eventsTodayResource ({'id':$scope.calendarId},
            function (response) {
                console.log('get list Events ',response);
                $scope.eventsList = response.items;
            }
        );


        endpointsService.eventCurrentResource({'id':$scope.calendarId},
            function(response){
                console.log('get Actual Event',response);
                console.log('get Actual Event start',response.start_date_time);
                console.log('get Actual Event end',response.end_date_time);
                var startTime = new Date(response.start_date_time);
                var endTime = new Date(response.end_date_time);
                response.duration = (endTime - startTime) / (60 * 1000)
                response.checkinURL = '';
                $scope.actual_event = response;
                $scope.countdownTimer  = $timeout($scope.onTimeout, 1000);
            }
        );
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

    $scope.getCheckinURL = function(isQR){
        var checkinURL = "/client/web/checkin?event_id=" +$scope.actual_event.id;
        if(isQR){
            checkinURL = window.location.protocol + window.api_host + checkinURL;
            return 'http://chart.apis.google.com/chart?cht=qr&chs=150x150&chl='+checkinURL+'&chld=H|0';
        }else
            return checkinURL;
    }

}]);
