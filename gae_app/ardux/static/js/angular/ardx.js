function api_init(){
    console.log("Initializing Endpoints Service");
    window.api = 'devices'
    window.version = 'v1'
    if(window.api_load){
        window.load_api = false;
        window.api_load(window.api, window.version);
    }else{
        window.load_api = true;
    }
}

window.app_host = window.location.host;

var ardx_app = angular.module('ardx_app', ['$strap.directives']);

ardx_app.config(function($interpolateProvider) {
	  $interpolateProvider.startSymbol('[[');
	  $interpolateProvider.endSymbol(']]');
});
