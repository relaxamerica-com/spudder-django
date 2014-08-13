var initialAddress,
    initialInfoWindowContent,
    maplocation;

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
           
           $.when(getLatLongDetail(location)).then(function(data) {
	           $('[name="state"]').val(data.state.short_name);
           });

            var infoWindowContent = '<div><strong>' + place.name + '</strong><br>' + address +
                '<br><a href="http://maps.google.com/?q=' + encodeURIComponent(address) + '" target="_new">External map</a>';
            infowindow.setContent(infoWindowContent);
            infowindow.open(map, marker);

            var inputInfoWindow = (document.getElementById('infoWindow'));
            inputInfoWindow.value = infoWindowContent;

            var locationInfoInput = document.getElementById('location_info'),
                locationInfo;

            locationInfo = location.lng() + ';' + location.lat() + ';';
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
            zoom: 3, center: new google.maps.LatLng(39.8282, -98.5795),
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

function createInfoWindow(name, address) {
	return '<div><strong>' + name + '</strong><br>' + address +
            '<br><a href="http://maps.google.com/?q=' + encodeURIComponent(address) + '" target="_new">External map</a>';
}

function getLatLongDetail(myLatlng) {
    var geocoder = new google.maps.Geocoder(),
    	deferred = new $.Deferred();
    	
    geocoder.geocode({ 'latLng': myLatlng },
      function (results, status) {
          if (status == google.maps.GeocoderStatus.OK) {
              if (results[0]) {
				  
				var address = "", city = "", state = "", zip = "", country = "", formattedAddress = "";
				var lat;
				var lng;

				for (var i = 0; i < results[0].address_components.length; i++) {
					var addr = results[0].address_components[i];
					// check if this entry in address_components has a type of country
					if (addr.types[0] == 'country')
						country = addr.long_name;
					else if (addr.types[0] == 'street_address')// address 1
						address = address + addr.long_name;
					else if (addr.types[0] == 'establishment')
						address = address + addr.long_name;
					else if (addr.types[0] == 'route')// address 2
						address = address + addr.long_name;
					else if (addr.types[0] == 'postal_code')// Zip
						zip = addr.short_name;
					else if (addr.types[0] == ['administrative_area_level_1']) {
						state = { 'long_name' : addr.long_name, 'short_name' : addr.short_name };
					}
					else if (addr.types[0] == ['locality'])// City
						city = addr.long_name;
				}

				if (results[0].formatted_address != null) {
					formattedAddress = results[0].formatted_address;
				}

				var location = results[0].geometry.location;

				lat = location.lat();
				lng = location.lng(); 


				deferred.resolve({
					'state' : state
				});

              }

          }

      });
      
  return deferred.promise();
}