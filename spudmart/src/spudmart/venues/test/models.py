from django.contrib.auth.models import User, AnonymousUser
from nose_plugins.noseplugins import FormattedOutputTestCase
from spudmart.venues.models import Venue, PendingVenueRental


class IsVenueAvailable(FormattedOutputTestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')

        self.venue = Venue(user=self.user1)
        self.venue.save()

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.venue.delete()

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
        self.venue.renter = self.user2

        self.assertFalse(self.venue.is_available())


class IsVenueRenter(FormattedOutputTestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')

        self.venue = Venue(user=self.user1)
        self.venue.renter = self.user2
        self.venue.save()

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.venue.delete()

    def test_user_is_not_logged_in(self):
        self.assertFalse(self.venue.is_renter(AnonymousUser))

    def test_venue_is_not_rented(self):
        self.venue.renter = None

        self.assertFalse(self.venue.is_renter(self.user2))

    def test_venue_is_rented_to_user(self):
        self.assertTrue(self.venue.is_renter(self.user2))

    def test_venue_is_rented_to_somebody_else(self):
        self.assertFalse(self.venue.is_renter(self.user1))


class IsVenueGroundsKeeper(FormattedOutputTestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')

        self.venue = Venue(user=self.user1)
        self.venue.save()

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.venue.delete()

    def test_user_is_not_logged_in(self):
        self.assertFalse(self.venue.is_renter(AnonymousUser))

    def test_is_venue_groundskeeper(self):
        self.assertTrue(self.venue.is_groundskeeper(self.user1))

    def test_is_not_venue_groundskeeper(self):
        self.assertFalse(self.venue.is_groundskeeper(self.user2))