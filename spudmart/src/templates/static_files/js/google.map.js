// Note: This example requires that you consent to location sharing when
// prompted by your browser. If you see a blank space instead of the map, this
// is probably because you have denied permission for location sharing.

var map;
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
			
			var response = $.post('/venues/save_coordinates/' + window.venueId, {
				'coordinates' : '' + position.coords.latitude + ',' + position.coords.longitude
			});
			
			response.done(function() {
				$('.buttons i.icon-map-marker').addClass('ready initialized');
			});
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
