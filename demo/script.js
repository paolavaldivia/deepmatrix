// Assuming we have an OpenSeadragon Viewer called "viewer", we can catch the clicks 
// with addHandler like so:

viewer.drawer.context.imageSmoothingEnabled = false;
viewer.drawer.context.mozImageSmoothingEnabled = false;
viewer.drawer.context.webkitImageSmoothingEnabled = false;
viewer.constrainDuringPan = true;

viewer.addHandler('open', function() {

        var tracker = new OpenSeadragon.MouseTracker({
            element: viewer.container,
            moveHandler: function(event) {
                var webPoint = event.position;
                var viewportPoint = viewer.viewport.pointFromPixel(webPoint);
                var imagePoint = viewer.viewport.viewportToImageCoordinates(viewportPoint);
                var zoom = viewer.viewport.getZoom(true);
                var imageZoom = viewer.viewport.viewportToImageZoom(zoom);

                console.log(imagePoint);
                // updateZoom();     
            }
        });  

        tracker.setTracking(true);
        // viewer.addHandler('animation', updateZoom);   
});