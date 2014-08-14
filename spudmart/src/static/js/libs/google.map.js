// Note: This example requires that you consent to location sharing when
// prompted by your browser. If you see a blank space instead of the map, this
// is probably because you have denied permission for location sharing.

window.map;

function getDistance(latitude1, longitude1, latitude2, longitude2) {
	var pos1 = new google.maps.LatLng(latitude1, longitude1),
		pos2 = new google.maps.LatLng(latitude2, longitude2);

	return google.maps.geometry.spherical.computeDistanceBetween(pos1, pos2);
}

function initialize(tryGeolocation, alertContainer, filter, successHandler) {
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
				content : 'Your Location' // window.venueName
			});

			google.maps.event.addListener(map, 'idle', function() {
				getVenuesWithinBounds().done(function(data) {

					var venues = JSON.parse(data).venues,
						otherVenueInRange = null,
						pos = position.coords;

					$.each(venues, function() {
						if (getDistance(this.latitude, this.longitude, pos.latitude, pos.longitude) <= 250
							&& filter(this)) {
							otherVenueInRange = this;
							return false;
						}
					});

					if (otherVenueInRange) {
						var venueLink = '<a href="/venues/view/'
										+ otherVenueInRange.id
										+ '">'
										+ otherVenueInRange.aka_name
										+ '</a>';
						showAlert(alertContainer, 'A ' + $('#venue-sport').val() + ' venue already exists near your current location: ' + venueLink, 'warning', false);
					} else {
						successHandler(pos.latitude, pos.longitude);
					}
				});
			});

			map.setCenter(pos);

		}, function() {
			handleNoGeolocation(true);
		});
	} else if (tryGeolocation) {
		// Browser doesn't support Geolocation
		handleNoGeolocation(false);
	} else {
		var	pos = new google.maps.LatLng(window.currentVenueLatitude, window.currentVenueLongitude);

		var infowindow = new google.maps.InfoWindow({
			map : map,
			position : pos,
			content : window.venueName
		});

		map.setCenter(pos);
	}

	google.maps.event.addListener(map,'bounds_changed', function() {
		getVenuesWithinBounds().done(function(data) {
			// console.log(data);
		});
	});

}

function getVenuesWithinBounds() {
	var NE =  map.getBounds().getNorthEast(),
		SW =  map.getBounds().getSouthWest();

	return response = $.get('/venues/get_venues_within_bounds', {
		'latitude_range' : [SW.lat(), NE.lat()],
		'longitude_range' : [SW.lng(), NE.lng()]
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