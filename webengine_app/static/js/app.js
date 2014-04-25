
var modules = [];
if(window.mode == 'admin'){
    modules = ['ui.bootstrap'];
}

var gApp = angular.module('gApp', modules, function($httpProvider)                                   {
	  // Use x-www-form-urlencoded Content-Type
	  $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8';
	  // Override $http service's default transformRequest
	  $httpProvider.defaults.transformRequest = [function(data)
	  {
	    /**
	     * The workhorse; converts an object to x-www-form-urlencoded serialization.
	     * @param {Object} obj
	     * @return {String}
	     */ 
	    var param = function(obj)
	    {
	      var query = '';
	      var name, value, fullSubName, subName, subValue, innerObj, i;
	      
	      for(name in obj)
	      {
	        value = obj[name];
	        
	        if(value instanceof Array)
	        {
	          for(i=0; i<value.length; ++i)
	          {
	            subValue = value[i];
	            fullSubName = name + '[' + i + ']';
	            innerObj = {};
	            innerObj[fullSubName] = subValue;
	            query += param(innerObj) + '&';
	          }
	        }
	        else if(value instanceof Object)
	        {
	          for(subName in value)
	          {
	            subValue = value[subName];
	            fullSubName = name + '[' + subName + ']';
	            innerObj = {};
	            innerObj[fullSubName] = subValue;
	            query += param(innerObj) + '&';
	          }
	        }
	        else if(value !== undefined && value !== null)
	        {
	          query += encodeURIComponent(name) + '=' + encodeURIComponent(value) + '&';
	        }
	      }
	      
	      return query.length ? query.substr(0, query.length - 1) : query;
	    };
	    
	    return angular.isObject(data) && String(data) !== '[object File]' ? param(data) : data;
	  }];
	  var $http,
	  interceptor = ['$q', '$injector', function ($q, $injector) {
          var notificationChannel;

          function success(response) {
              // get $http via $injector because of circular dependency problem
              $http = $http || $injector.get('$http');
              // don't send notification until all requests are complete
              if ($http.pendingRequests.length < 1) {
                  // get requestNotificationChannel via $injector because of circular dependency problem
                  notificationChannel = notificationChannel || $injector.get('requestNotificationChannel');
                  // send a notification requests are complete
                  notificationChannel.requestEnded();
              }
              return response;
          }

          function error(response) {
              // get $http via $injector because of circular dependency problem
              $http = $http || $injector.get('$http');
              // don't send notification until all requests are complete
              if ($http.pendingRequests.length < 1) {
                  // get requestNotificationChannel via $injector because of circular dependency problem
                  notificationChannel = notificationChannel || $injector.get('requestNotificationChannel');
                  // send a notification requests are complete
                  notificationChannel.requestEnded();
              }
              return $q.reject(response);
          }

          return function (promise) {
              // get requestNotificationChannel via $injector because of circular dependency problem
              notificationChannel = notificationChannel || $injector.get('requestNotificationChannel');
              // send a notification requests are complete
              notificationChannel.requestStarted();
              return promise.then(success, error);
          }
      }];

	  $httpProvider.responseInterceptors.push(interceptor);
});

gApp.factory('requestNotificationChannel', ['$rootScope', function($rootScope){
    // private notification messages
    var _START_REQUEST_ = '_START_REQUEST_';
    var _END_REQUEST_ = '_END_REQUEST_';

    // publish start request notification
    var requestStarted = function() {
        $rootScope.$broadcast(_START_REQUEST_);
    };
    // publish end request notification
    var requestEnded = function() {
        $rootScope.$broadcast(_END_REQUEST_);
    };
    // subscribe to start request notification
    var onRequestStarted = function($scope, handler){
        $scope.$on(_START_REQUEST_, function(event){
            handler();
        });
    };
    // subscribe to end request notification
    var onRequestEnded = function($scope, handler){
        $scope.$on(_END_REQUEST_, function(event){
            handler();
        });
    };

    return {
        requestStarted:  requestStarted,
        requestEnded: requestEnded,
        onRequestStarted: onRequestStarted,
        onRequestEnded: onRequestEnded
    };
}]);

gApp.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('[[');
	$interpolateProvider.endSymbol(']]');
});

function randomString(length, chars) {
	if(chars == undefined){
		chars ='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	}
    var result = '';
    for (var i = length; i > 0; --i) result += chars[Math.round(Math.random() * (chars.length - 1))];
    return result;
}

String.prototype.visualLength = function()
{
    //var ruler = document.getElementById("ruler");
    //ruler.innerHTML = this;
    //return ruler.offsetWidth;
    return 100;
}

function makeid()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}