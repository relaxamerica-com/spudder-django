function initWithCoords(latitude, longitude){
    var jumbo_map = new google.maps.Map($('#jumbo-map-container')[0], {
        zoom: 19,
        mapTypeId: 'satellite',
        scrollwheel: false,
        navigationControl: false,
        mapTypeControl: false,
        scaleControl: false,
        draggable: false,
        disableDefaultUI: true,
        center: new google.maps.LatLng(latitude, longitude)
    });
}

function initWithAddr(addr){
    geocoder = new google.maps.Geocoder();
    geocoder.geocode({
        'address': addr
    }, function(results, status){
        if (status == google.maps.GeocoderStatus.OK){
            var jumbo_map = new google.maps.Map($('#jumbo-map-container')[0], {
                zoom: 19,
                mapTypeId: 'satellite',
                scrollwheel: false,
                navigationControl: false,
                mapTypeControl: false,
                scaleControl: false,
                draggable: false,
                disableDefaultUI: true,
                center: results[0].geometry.location
            });
        }
    });
}