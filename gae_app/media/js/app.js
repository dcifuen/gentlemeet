initialize = function(apiRoot) {
    var apisToLoad;
    var callback = function() {
        if (--apisToLoad == 0) {
            //bootstrap manually angularjs after our api are loaded
            angular.bootstrap(document, [ "license_app" ]);
        }
    }
    apisToLoad = 1; // must match number of calls to gapi.client.load()
    gapi.client.load('devices', 'v1', callback, apiRoot);
};

var license_app = angular.module('license_app', []);

license_app.config(function($interpolateProvider) {
      $interpolateProvider.startSymbol('{[{');
      $interpolateProvider.endSymbol('}]}');
});