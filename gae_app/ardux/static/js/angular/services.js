ardx_app.service('EndpointsService',function($q, $rootScope, $http, $window) {

    var service = this;
    service.ENDPOINTS_READY = "ENDPOINTS_READY";
    /**
     * build service methods from discovery document
     * @param api
     * @param resource
     * @param method
     * @returns {Function}
     */
    var builder = function (api, resource, method){
        return function (args, callback) {
              var deferred = $q.defer();
              gapi.client[api][resource][method](args).execute(function(resp) {
                  callback(resp);
                  $rootScope.$apply(deferred.resolve(resp));
              });

              return deferred.promise;
        };
    }

    /**
     * brings the discovery document and adds methods in the service built from the information brought
     * @param api
     * @param version
     */
    service.loadService = function(api, version, callback){
        service.apiName = api;
        service.apiVersion = version;

        var apiRoot = $window.app_host + '/_ah/api';
        if(apiRoot.indexOf("localhost")>=0){
            apiRoot = "http://"+apiRoot;
        }else{
            apiRoot = "https://"+apiRoot;
        }
        console.log("Configuring api "+apiRoot);
        gapi.client.load(service.apiName, service.apiVersion, function() {
            var apiUrl = '';
            $http.get(apiRoot+'/discovery/v1/apis/'+service.apiName+'/'+service.apiVersion+'/rest').success(function(data) {
                for (resource in data.resources){
                    for(method in data.resources[resource].methods){
                        var capitalizedResource = resource[0].toUpperCase() + resource.substring(1);
                        service[method+capitalizedResource] = builder(service.apiName, resource,  method);
                        console.log("Method "+method+capitalizedResource+" created");
                    }
                }
                callback();
            });
            $rootScope.$$phase || $rootScope.$apply();
        }, apiRoot);
    }

    $window.api_load = function(api, version){
        service.loadService(api, version, function(){
            console.log("Endpoints Service Ready")
            $rootScope.$broadcast(service.ENDPOINTS_READY);console
        });
    }

    if($window.load_api){
        $window.api_load($window.api, $window.version);
    }

});
