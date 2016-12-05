/**
 * Created by pao on 12/5/16.
 */


var Util = function() {
};


Util.buildQuery = function(url, params){
  var rQuery = url + $.param(params);
  return rQuery;
}

Util.parseJson =  function (data) {
  return $.parseJSON(data);
}

Number.prototype.between = function(a, b) {
  var min = Math.min.apply(Math, [a, b]),
    max = Math.max.apply(Math, [a, b]);
  return this > min && this < max;
};
