from spudmart.donations.models import RentVenue, DonationState
from spudmart.utils.querysets import get_object_or_none
from spudmart.venues.models import PendingVenueRental
from spudmart.sponsors.models import SponsorPage

def finalize_pending_rentals(pending_rentals, role):
    """
    Finalizes pending Venue rentals.

    :param pending_rentals: string representing list of pending rentals, separated by comma
    :return: number of finalized rentals
    """
    if not pending_rentals:
        return 0

    venues = pending_rentals.split(',')
    count = 0

    sponsor = SponsorPage.objects.get(id=role.entity_id)

    for venue_id in venues:
        pending_venue = get_object_or_none(PendingVenueRental, pk=venue_id)
        if pending_venue:
            count += 1

            venue = pending_venue.venue
            venue.sponsor = sponsor
            venue.save()

            rent_venue = RentVenue.objects.get(venue=venue)
            rent_venue.donor = role.user
            rent_venue.state = DonationState.FINISHED
            rent_venue.save()

            pending_venue.delete()

    return count