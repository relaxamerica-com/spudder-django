from django.contrib.auth.models import User, AnonymousUser
from nose_plugins.noseplugins import FormattedOutputTestCase
from spudmart.sponsors.models import SponsorPage
from spudmart.venues.models import Venue, PendingVenueRental


class IsVenueAvailable(FormattedOutputTestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')

        self.sponsor_page = SponsorPage(sponsor=self.user2)
        self.sponsor_page.save()

        self.venue = Venue(user=self.user1)
        self.venue.save()

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()

    def test_price_is_not_specified(self):
        self.venue.price = 0.0

        self.assertFalse(self.venue.is_available())

    def test_price_is_set_and_nobody_rented_it(self):
        self.venue.price = 2.0

        self.assertTrue(self.venue.is_available())

    def test_somebody_rented_venue_but_transaction_is_pending(self):
        self.venue.price = 2.0

        PendingVenueRental(venue=self.venue).save()

        self.assertFalse(self.venue.is_available())

    def test_price_is_set_and_somebody_rented_it(self):
        self.venue.price = 2
        self.venue.renter = self.sponsor_page

        self.assertFalse(self.venue.is_available())