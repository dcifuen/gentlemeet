gApp.controller('checkinCtrl', ['$scope', '$timeout','EndpointsService', function ($scope, $timeout, endpointsService) {

    $scope.CLIENT_ID = "";
    $scope.SCOPES = "https://www.googleapis.com/auth/userinfo.email"
    $scope.event_id = getURLParameter('event_id');
    $scope.url_callback = getURLParameter('callback');
    $scope.is_checked = null;


    $scope.$on(endpointsService.ENDPOINTS_READY, function () {
        //load tags
        console.log("Endpoints ready...");

        if($scope.event_id){
            endpointsService.authorize($scope.CLIENT_ID, $scope.SCOPES, $scope.auth_callback);
        }
    });

    $scope.after_checking = function(){
        $scope.is_checked = true;
        if($scope.url_callback){
            window.location.assign($scope.url_callback);
        }
    }

    $scope.auth_callback = function(){
      console.log("Auth ready");
      endpointsService.checkInEvents({'id': $scope.event_id},function (response) {
          console.log(response);
          if(response.error){
              console.error("error checking",response.error );

              if(response.error.code == 400 && response.error.message == 'User have already checked in'){
                  $scope.after_checking()
              }

          }else{
              $scope.after_checking()
          }
      });
    };
}]);


function getURLParameter(name) {
  return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}
