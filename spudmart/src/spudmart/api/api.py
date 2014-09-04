from spudmart.venues.models import Venue


def get_venues():
    venues = Venue.objects.all()
    venues_json = []
    for venue in venues:
        venues_json.append({
            'id': venue.id,
            'lat': str(venue.latitude),
            'lon': str(venue.longitude),
            'sport': venue.sport})
    return_json = {'venues': venues_json}
    return return_json