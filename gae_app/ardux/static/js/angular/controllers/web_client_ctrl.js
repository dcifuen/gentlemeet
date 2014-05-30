gApp.controller('testCtrl', ['$scope', '$timeout','EndpointsService', function ($scope, $timeout, endpointsService) {
    $scope.getSecondsAsDate = function(seconds){
        return moment().startOf('day').add('s', seconds).toDate();
    };

    $scope.countdownTimer = null;
    $scope.calendarId = '-60841444955'; //Should be device Id

    $scope.disable_quick_add = false;
    $scope.disable_finish_event = false;




    $scope.events_today_resource = function(){
        endpointsService.nextEventsTodayResource ({'id':$scope.calendarId},
            function (response) {
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
    }

    $scope.quick_add = function(){
        if(!$scope.disable_quick_add){
           $scope.disable_quick_add = true;
            endpointsService.quickAddResource ({'id':$scope.calendarId},function (response) {
                if(response.error){
                    console.log('Error in quick add', response);
                }
            });
        }
    }

    $scope.event_current_resource = function(){
        endpointsService.eventCurrentResource({'id':$scope.calendarId},
            function(response){
                if(response.error){
                    $scope.actual_event = null;
                }else{
                    $scope.disable_quick_add = false;
                    var startTime = new Date(response.start_date_time);
                    var endTime = new Date(response.end_date_time);
                    var now = new Date();

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

                    if(!$scope.actual_event ||
                        ($scope.actual_event && response.id && response.id != $scope.actual_event.id)
                      ){
                        $scope.disable_finish_event = false;
                        $scope.actual_event = response;
                        $scope.countdownTimer  = $timeout($scope.onTimeout, 1000);
                    }
                }
            }
        );
    }


    $scope.$on(endpointsService.ENDPOINTS_READY, function () {
        //load tags
        console.log("Endpoints ready...");
        $scope.events_today_resource();
        $scope.event_current_resource();

        setInterval($scope.events_today_resource,2000);
        setInterval($scope.event_current_resource,30000);
    });


    $scope.onTimeout = function(){
        if($scope.actual_event && $scope.actual_event.duration >0){
            $scope.actual_event.duration--;
            $scope.countdownTimer = $timeout($scope.onTimeout, 1000);
        }else{
            $scope.finish_event();
            $scope.actual_event = null;
        }
    }

    $scope.finish_event= function(){
        $scope.disable_finish_event = true;
        if($scope.actual_event){
            endpointsService.finishEvent({'id':$scope.actual_event.id}, function(response){

                console.log(response);

                console.log('Event was finished')
            });
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
                checkinURL = window.location.protocol +'//' +  window.api_host + checkinURL;
                return 'http://chart.apis.google.com/chart?cht=qr&chs=150x150&chl='+checkinURL+'&chld=H|0';
            }else{
                return checkinURL;
            }
        }else{
            return '#';
        }
    }

}]);
