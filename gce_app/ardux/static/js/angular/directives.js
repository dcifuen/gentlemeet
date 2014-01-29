atbt_app.directive('ngBlur', ['$parse', function($parse) {
  return function(scope, element, attr) {
    var fn = $parse(attr['ngBlur']);
    element.bind('blur', function(event) {
      scope.$apply(function() {
        fn(scope, {$event:event});
      });
    });
  }
}]);

atbt_app.directive('uppercase', function() {
   return {
     require: 'ngModel',
     link: function(scope, element, attrs, modelCtrl) {
        var uppercase = function(inputValue) {
            if (inputValue){
               var uppercase = inputValue.toUpperCase();
               if(uppercase !== inputValue) {
                  modelCtrl.$setViewValue(uppercase);
                  modelCtrl.$render();
                }
                return uppercase;
            }else{
                return inputValue
            }
         }
         modelCtrl.$parsers.push(uppercase);
         uppercase(scope[attrs.ngModel]);  // uppercase initial value
     }
   };
});

atbt_app.directive('digits', function() {
  return {
    require: 'ngModel',
    link: function(scope, elm, attrs, ctrl) {
      ctrl.$parsers.unshift(function(viewValue) {
          var digits = attrs.digits
        if(viewValue.length == digits){
            ctrl.$setValidity('digits', true);
        }else{
            ctrl.$setValidity('digits', false);
        }
        return viewValue;
      });
    }
  };
});