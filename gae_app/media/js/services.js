license_app.service('CustomerService',function($q, $rootScope) {

  this.listCustomers = function() {
      var deferred = $q.defer();
      gapi.client.customer.customer.list().execute(function(resp) {
         $rootScope.$apply(deferred.resolve(resp.items));
      });
      return deferred.promise;
  };

  this.insertCustomer = function(name, domain) {
      var deferred = $q.defer();
      gapi.client.customer.customer.insert({'name':name,'domain':domain}).execute(function(resp) {
         $rootScope.$apply(deferred.resolve(resp));
      });
      return deferred.promise;
  };
});

license_app.service('ProductService', function($q, $rootScope) {

    this.listProducts = function(callback) {
        var deferred = $q.defer();
        gapi.client.product.product.list().execute(function(resp) {
            $rootScope.$apply(deferred.resolve(resp.items));
        });
        return deferred.promise;
    };

    this.insertProduct = function(name, code, price) {
          var deferred = $q.defer();
          gapi.client.product.product.insert({'name':name, 'code':code, 'price':price}).execute(function(resp) {
             $rootScope.$apply(deferred.resolve(resp));
          });
          return deferred.promise;
      };

});
