atbt_app.service('EndpointService',function($q, $rootScope, $http) {

    var service = this;
    var http = $http;
    var builder = function (api, resource, method){
        return function (args,callback) {
              var deferred = $q.defer();
              gapi.client[api][resource][method](args).execute(function(resp) {
                 $rootScope.$apply(deferred.resolve(resp));
              });
              deferred.promise.then(callback)
              return deferred.promise;
        };
    }
    var loaded = false;
    this.isLoaded = function() { return loaded; };

    this.loadService = function(api, version){
        service.apiName = api;
        service.apiVersion = version;
        //Check whether in production, staging or local
        var isProduction = (window.location.host == 'www-atbt.appspot.com') || ( window.location.host == 'ardux.eforcers.com');
        var isStaging = window.location.host.indexOf("-staging") != -1;
        var serverURL = window.location.host;
        if (isProduction){
            serverURL = 'www-atbt.appspot.com';
        } else if(isStaging){
            serverURL = serverURL.replace('-staging.', '-staging-dot-');
        }
        console.log('Is in production? ['+ isProduction +'] staging? ['+isStaging+'] Server URL ['+serverURL+']');

        var apiRoot = '';
        if (isProduction || isStaging){
            apiRoot= 'https://' + serverURL + '/_ah/api';
        } else {
            apiRoot= '//' + window.location.host + '/_ah/api';
        }

        gapi.client.load(service.apiName, service.apiVersion, function() {
            var apiUrl = '';
            http.get(apiRoot+'/discovery/v1/apis/'+service.apiName+'/'+service.apiVersion+'/rest').success( function(data) {
                console.log(data);
                for (resource in data.resources){
                    for(method in data.resources[resource].methods){
                        service[method+resource] = builder(service.apiName,resource,  method);
                        console.log("Method "+method+resource+" created");
                    }
                }
                loaded = true;
            });
            $rootScope.$$phase || $rootScope.$apply();
        }, apiRoot);
    }
});