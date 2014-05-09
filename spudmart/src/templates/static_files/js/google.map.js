// Note: This example requires that you consent to location sharing when
// prompted by your browser. If you see a blank space instead of the map, this
// is probably because you have denied permission for location sharing.

window.map;

function getDistance( $latitude1, $longitude1, $latitude2, $longitude2 )
{  
    $earth_radius = 6371;

    $dLat = deg2rad( $latitude2 - $latitude1 );  
    $dLon = deg2rad( $longitude2 - $longitude1 );  

    $a = sin($dLat/2) * sin($dLat/2) + cos(deg2rad($latitude1)) * cos(deg2rad($latitude2)) * sin($dLon/2) * sin($dLon/2);  
    $c = 2 * asin(sqrt($a));  
    $d = $earth_radius * $c;  

    return $d;  
}

function initialize(tryGeolocation) {
	var mapOptions = {
		zoom : 15
	};
	map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

	// Try HTML5 geolocation
	if (tryGeolocation && navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(function(position) {
			var pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);

			var infowindow = new google.maps.InfoWindow({
				map : map,
				position : pos,
				content : window.venueName
			});

			map.setCenter(pos);
			
		}, function() {
			handleNoGeolocation(true);
		});
	} else if (tryGeolocation) {
		// Browser doesn't support Geolocation
		handleNoGeolocation(false);
	} else {
		var coordinates = window.coordinates.split(','),
			pos = new google.maps.LatLng(coordinates[0], coordinates[1]);
			
		var infowindow = new google.maps.InfoWindow({
			map : map,
			position : pos,
			content : window.venueName
		});
		
		map.setCenter(pos);
	}
	
	google.maps.event.addListener(map,'bounds_changed', function() {
		var NE =  map.getBounds().getNorthEast(),
			SW =  map.getBounds().getSouthWest();
		
		var response = $.get('/venues/get_venues_within_bounds', {
			'latitude_range' : SW.lat() + '|' + NE.lat(),
			'longitude_range' : SW.lng() + '|' + NE.lng()
		});
		
		response.done(function(data) {
			console.log(data);
		});
	});
	
	
}

function handleNoGeolocation(errorFlag) {
	if (errorFlag) {
		var content = 'Error: The Geolocation service failed.';
	} else {
		var content = 'Error: Your browser doesn\'t support geolocation.';
	}

	var options = {
		map : map,
		position : new google.maps.LatLng(60, 105),
		content : content
	};

	var infowindow = new google.maps.InfoWindow(options);
	map.setCenter(options.position);
}

// google.maps.event.addDomListener(window, 'load', initialize);
