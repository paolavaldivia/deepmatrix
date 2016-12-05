// Assuming we have an OpenSeadragon Viewer called "viewer", we can catch the clicks 
// with addHandler like so:


(function(){
  var xhttp = new XMLHttpRequest();
  var url = 'http://localhost:5000/matrixinfo?';

  viewer.drawer.context.imageSmoothingEnabled = false;
  viewer.drawer.context.mozImageSmoothingEnabled = false;
  viewer.drawer.context.webkitImageSmoothingEnabled = false;
  viewer.constrainDuringPan = true;

  viewer.addHandler('open', function() {

    var imageSize = viewer.viewport._contentSize;

    var tracker = new OpenSeadragon.MouseTracker({
      element: viewer.container,
      moveHandler: function(event) {
        var webPoint = event.position;
        var viewportPoint = viewer.viewport.pointFromPixel(webPoint);
        var imagePoint = viewer.viewport.viewportToImageCoordinates(viewportPoint);
        // var zoom = viewer.viewport.getZoom(true);
        // var imageZoom = viewer.viewport.viewportToImageZoom(zoom);

        if(imagePoint.y.between(0, imageSize.y) && imagePoint.x.between(0, imageSize.x)){
          var mousePos = {'x': event.originalEvent.pageX, 'y': event.originalEvent.pageY};
          var imagePos = {'x': Math.floor(imagePoint.x), 'y': Math.floor(imagePoint.y)};
          $(EventManager).trigger("imageHover", [mousePos, imagePos]);
        }
        else {
          $(EventManager).trigger("imageExit");
        }
        // updateZoom();
      },
      exitHandler: function () {
        $(EventManager).trigger("imageExit");
      }

    });

    tracker.setTracking(true);
    // viewer.addHandler('animation', updateZoom);
  });

  var updateTooltip = function(mousePos, imageInfo){
    $('#tooltip')
      .css({"top": (mousePos.y-40)+"px", "left": mousePos.x-10+"px"})
      .css("visibility", "visible");
    $('#tooltip-text').text(imageInfo.x + " " + imageInfo.y);
  }

  var imageHoverHandler = function(event, mousePos, imagePoint){
    var query = {'mpx': mousePos.x, 'mpy': mousePos.y, 'ipx': imagePoint.x, 'ipy':imagePoint.y };
    var rQuery = Util.buildQuery(url, query);
    console.log(rQuery);

    xhttp.open("GET", rQuery, true);
    xhttp.send();

    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var response = Util.parseJson(this.responseText);
        var mousePos = response.mousePos;
        var imageInfo = response.imageInfo;
       updateTooltip(mousePos, imageInfo);
      }
    };

  }

  var imageExitHandler = function(){
    $('#tooltip')
      .css("visibility", "hidden");
  }

  $(EventManager).bind("imageHover", imageHoverHandler);
  $(EventManager).bind("imageExit", imageExitHandler);

})();
