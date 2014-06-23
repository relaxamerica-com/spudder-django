from django.contrib.auth.models import User
from nose_plugins.noseplugins import FormattedOutputTestCase
from spudmart.donations.models import RentVenue, DonationState
from spudmart.venues.models import Venue, PendingVenueRental
from spudmart.venues.utils import finalize_pending_rentals


class FinalizePendingRentals(FormattedOutputTestCase):
    fixtures = ['users.json', 'pending_rentals.json']

    def setUp(self):
        self.renter = User.objects.get(pk=2)

    def test_no_pending_rentals_passed(self):
        count = finalize_pending_rentals(None, None)

        self.assertEquals(0, count)

    def test_no_pending_rentals(self):
        count = finalize_pending_rentals('', None)

        self.assertEquals(0, count)

    def test_single_rental(self):
        count = finalize_pending_rentals('104', self.renter)

        self.assertEquals(1, count)

        venue = Venue.objects.get(pk=100)
        rent_venue = RentVenue.objects.get(pk=101)
        self.assertEquals(venue.renter, self.renter)
        self.assertEquals(rent_venue.donor, self.renter)
        self.assertEquals(rent_venue.state, DonationState.FINISHED)

        self.assertEquals(0, PendingVenueRental.objects.filter(venue=venue).count())

    def test_multiple_rentals(self):
        count = finalize_pending_rentals('104,105', self.renter)

        self.assertEquals(2, count)

        venue = Venue.objects.get(pk=100)
        rent_venue = RentVenue.objects.get(pk=101)
        self.assertEquals(venue.renter, self.renter)
        self.assertEquals(rent_venue.donor, self.renter)
        self.assertEquals(rent_venue.state, DonationState.FINISHED)

        venue = Venue.objects.get(pk=102)
        rent_venue = RentVenue.objects.get(pk=103)
        self.assertEquals(venue.renter, self.renter)
        self.assertEquals(rent_venue.state, DonationState.FINISHED)
        self.assertEquals(rent_venue.donor, self.renter)

        self.assertEquals(0, PendingVenueRental.objects.all().count())
