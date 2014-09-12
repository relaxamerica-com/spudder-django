function get_map_container(){
    var $map_container = $('#jumbo-map-container');
    if ($map_container.length == 0)
        return null;
    if ($map_container.is('.spudder-jumbotron')){
        var $new_map_container = $("<div></div>");
        $new_map_container.addClass('spudder-jumbotron-map');
        $new_map_container.css({height: '100%', width: '100%'});
        $new_map_container.prependTo($map_container);
        return $map_container.find('.spudder-jumbotron-map')[0];
    }
    return $map_container[0];
}

function initWithCoords(latitude, longitude){
    var $map_container = get_map_container();
    if ($map_container == null)
        return;
    var jumbo_map = new google.maps.Map($map_container, {
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

            var $map_container = get_map_container();
            if ($map_container == null)
                return;
            var jumbo_map = new google.maps.Map($map_container, {
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