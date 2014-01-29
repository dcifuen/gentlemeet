function init() {
  window.init();
}

var atbt_app = angular.module('atbt_app', ['$strap.directives']);

atbt_app.config(function($interpolateProvider) {
	  $interpolateProvider.startSymbol('{[{');
	  $interpolateProvider.endSymbol('}]}');
});
