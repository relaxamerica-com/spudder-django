from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.test import Client
from nose_plugins.noseplugins import FormattedOutputTestCase
import mock


class SignInComplete(FormattedOutputTestCase):
    fixtures = ['users.json', 'pending_rentals.json']

    def setUp(self):
        self.client = Client()

    def test_no_pending_transaction_in_session(self):
        response = self.client.get('/venues/rent_venue/sign_in_complete')

        self.assertRedirects(
            response, '/',
            status_code=HttpResponseRedirect.status_code,  # this redirect comes from tested view
            target_status_code=HttpResponseRedirect.status_code  # this redirect comes from temp_redirect_view
        )

    def test_single_pending_transaction(self):
        with mock.patch('spudmart.venues.utils.finalize_pending_rentals', return_value=1) as fake_func:
            user = User.objects.get(pk=2)
            self.client.login(username='user2', password='user2')

            session = self.client.session
            session['pending_venues_rental'] = '104'
            session.save()

            response = self.client.get('/venues/rent_venue/sign_in_complete')

            self.assertRedirects(
                response, '/dashboard/sponsor/page',
                status_code=HttpResponseRedirect.status_code,  # this redirect comes from tested view
                target_status_code=HttpResponseRedirect.status_code  # this redirect comes from temp_redirect_view
            )

            fake_func.assert_called_once_with('104', user)

            self.assertFalse('pending_venues_rental' in self.client.session)

    def test_multiple_pending_transactions(self):
        with mock.patch('spudmart.venues.utils.finalize_pending_rentals', return_value=2) as fake_func:
            user = User.objects.get(pk=2)
            self.client.login(username='user2', password='user2')

            session = self.client.session
            session['pending_venues_rental'] = '104,105'
            session.save()

            response = self.client.get('/venues/rent_venue/sign_in_complete')

            self.assertRedirects(
                response, '/dashboard/sponsor/page',
                status_code=HttpResponseRedirect.status_code,  # this redirect comes from tested view
                target_status_code=HttpResponseRedirect.status_code  # this redirect comes from temp_redirect_view
            )

            fake_func.assert_called_once_with('104,105', user)

            self.assertFalse('pending_venues_rental' in self.client.session)