var initialAddress,
    initialInfoWindowContent;

function initialize() {
    function addPlaceChangedListener() {
        google.maps.event.addListener(autocomplete, 'place_changed', function () {
            infowindow.close();
            marker.setVisible(false);

            var place = autocomplete.getPlace();
            if (!place.geometry) return;

            var location = place.geometry.location;

            if (place.geometry.viewport) {
                map.fitBounds(place.geometry.viewport);
            } else {
                map.setCenter(location);
                map.setZoom(17);  // Why 17? Because it looks good.
            }

            marker.setPosition(location);
            marker.setVisible(true);

            var address = '';
            if (place.address_components) {
                address = [
                    (place.address_components[0] && place.address_components[0].short_name || ''),
                    (place.address_components[1] && place.address_components[1].short_name || ''),
                    (place.address_components[2] && place.address_components[2].short_name || '')
                ].join(' ');
            }

            var infoWindowContent = '<div><strong>' + place.name + '</strong><br>' + address +
                '<br><a href="http://maps.google.com/?q=' + encodeURIComponent(address) + '" target="_new">External map</a>';
            infowindow.setContent(infoWindowContent);
            infowindow.open(map, marker);

            var inputInfoWindow = (document.getElementById('infoWindow'));
            inputInfoWindow.value = infoWindowContent;

            var locationInfoInput = document.getElementById('location_info'),
                locationInfo;

            locationInfo = location.B + ';' + location.k + ';';
            locationInfo += infoWindowContent + ';';
            locationInfo += address;

            locationInfoInput.value = locationInfo;
        });
    }

    function addKeyDownListener() {
        google.maps.event.addDomListener(input, 'keydown', function (event) { // Prevent form submit event on Enter
            if (event.keyCode == 13) {
                if (event.preventDefault) {
                    event.preventDefault();
                } else {
                    event.cancelBubble = true;
                    event.returnValue = false;
                }
            }
        });
    }

    function placeStartMarker (address, infoWindow) {
        var geocoder = new google.maps.Geocoder();

        geocoder.geocode({ 'address': address}, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                var location = results[0].geometry.location;

                map.setCenter(location);
                map.setZoom(13);

                marker.setPosition(location);
                marker.setVisible(true);

                infowindow.setContent(infoWindow);
                input.value = address;
                infowindow.open(map, marker);
            }
        });
    }

    var mapOptions = {
            zoom: 6, center: new google.maps.LatLng(-34.397, 150.644),
                mapTypeControl: false, streetViewControl: false
        },
        canvas = document.getElementById('map_canvas'),
        map = new google.maps.Map(canvas, mapOptions),
        input = (document.getElementById('location'));

    addKeyDownListener();

    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

    var autocomplete = new google.maps.places.Autocomplete(input);
    window.autocomplete = autocomplete;
    autocomplete.bindTo('bounds', map);

    var infowindow = new google.maps.InfoWindow(),
        marker = new google.maps.Marker({ map: map });

    addPlaceChangedListener();

    if (initialAddress && initialInfoWindowContent) {
        placeStartMarker(initialAddress, initialInfoWindowContent);
    }
}

function initializeGoogleMaps(address, infoWindow) {
    initialAddress = address;
    initialInfoWindowContent = infoWindow;

    google.maps.event.addDomListener(window, 'load', initialize);
}