customerCtrl = license_app.controller('customerCtrl', function ($scope, CustomerService) {
    $scope.loadCustomers = function(){
        var promise = CustomerService.listCustomers();
        promise.then(function(customers) {
            $scope.customers = customers
        });
    };

    $scope.addCustomer = function(){
        var promise = CustomerService.insertCustomer($scope.newName, $scope.newDomain);
        promise.then(function(customer) {
            $scope.newName = ""
            $scope.newDomain = ""
            $scope.loadCustomers();
        });

    };


    $scope.loadCustomers();
});

customerCtrl.$inject = ['$scope','CustomerService'];

productCtrl = license_app.controller('productCtrl', function ($scope, ProductService) {
    $scope.loadProducts = function(){
        var promise = ProductService.listProducts();
        promise.then(function(products) {
            $scope.products = products
        });
    };

    $scope.addProduct = function(){
        var promise = ProductService.insertProduct($scope.newName, $scope.newCode, $scope.newPrice);
        promise.then(function(product) {
            $scope.newName = ""
            $scope.newCode = ""
            $scope.newPrice = ""
            $scope.loadProducts();
        });

    };

    $scope.loadProducts();
});

productCtrl.$inject = ['$scope','ProductService'];