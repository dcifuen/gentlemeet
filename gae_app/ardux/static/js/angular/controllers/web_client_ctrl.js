gApp.controller('testCtrl', ['$scope', '$timeout','EndpointsService', function ($scope, $timeout, endpointsService) {
    $scope.getSecondsAsDate = function(seconds){
        return moment().startOf('day').add('s', seconds).toDate();
    };

    $scope.countdownTimer = null;
    $scope.calendarId = '-60841444955'; //Should be device Id

    $scope.$on(endpointsService.ENDPOINTS_READY, function () {
        //load tags
        console.log("Endpoints ready...");


        endpointsService.nextEventsTodayResource ({'id':$scope.calendarId},
            function (response) {
                console.log("error",response);
                if(response.error){
                    $scope.eventsList = []
                }else{
                     if(response.items){
                        response.items.forEach(function(item) {
                            item.startTime = new Date(item.start_date_time);
                            item.endTime = new Date(item.end_date_time);
                        });

                        $scope.eventsList = response.items;
                    }else{
                       $scope.eventsList = []
                    }
                }
            }
        );


        endpointsService.eventCurrentResource({'id':$scope.calendarId},
            function(response){
                if(response.error){
                    $scope.actual_event = null;
                }else{
                    var startTime = new Date(response.start_date_time);
                    var endTime = new Date(response.end_date_time);
                    var now = new Date();
                    console.log('now',now);
                    console.log('endTime',endTime);
                    console.log('endTime - now',endTime - now);

                    response.duration = (endTime - now) / 1000
                    response.checkinURL = '';
                    response.startTimeAux = startTime;
                    response.endTimeAux = endTime;
                    response.total_attendees = [];
                    if(!response.actual_attendees){
                        response.actual_attendees = [];
                    }

                    if(response.no_response_attendees){
                        response.total_attendees = response.total_attendees.concat(response.no_response_attendees);
                    }
                    if(response.yes_attendees){
                        response.total_attendees = response.total_attendees.concat(response.yes_attendees);
                    }
                    if(response.maybe_attendees){
                        response.total_attendees = response.total_attendees.concat()
                    }



                    $scope.actual_event = response;
                    $scope.countdownTimer  = $timeout($scope.onTimeout, 1000);
                }
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
        if($scope.actual_event){
            var checkinURL = "/client/web/checkin?event_id=" + $scope.actual_event.id;
            if(isQR){
                checkinURL = window.location.protocol + window.api_host + checkinURL;
                return 'http://chart.apis.google.com/chart?cht=qr&chs=150x150&chl='+checkinURL+'&chld=H|0';
            }else{
                return checkinURL;
            }
        }else{
            return '';
        }
    }

}]);
