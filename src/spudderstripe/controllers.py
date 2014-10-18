import logging
import traceback
from requests.packages.urllib3.exceptions import DecodeError
from simplejson.decoder import JSONDecodeError
from spudderstripe.api_utils import create_customer, create_token, make_charge
import httplib
import json
import urllib
from django.conf import settings
from settings import Environments
import stripe


class StripeRecipientsControllerException(Exception):
    def __init__(self):
        pass


class StripeRecipientsController(object):
    """
    :raises StripeRecipientsControllerException when anything goes wrong with access token update action
    """

    def __init__(self, stripe_recipient, stripe_user):
        self.stripe_recipient = stripe_recipient
        self.stripe_user = stripe_user
        self._update_access_token()

    def _update_access_token(self):
        exception_occurred = False

        try:
            params = urllib.urlencode({
                'client_secret': settings.STRIPE_SECRET_KEY,
                'refresh_token': self.stripe_user.refresh_token,
                'grant_type': 'refresh_token'})
            url = '/oauth/token?%s' % params

            connection = httplib.HTTPSConnection('connect.stripe.com')
            connection.connect()
            connection.request('POST', url)
            stripe_response = connection.getresponse()

            response_data = stripe_response.read()

            json_data = json.loads(response_data)

            self.stripe_user.access_token = json_data['access_token']
            self.stripe_user.save()
        except httplib.HTTPException:
            exception_occurred = True
            logging.error('Http connection exception while trying to contact Stripe API server')
        except DecodeError:
            exception_occurred = True
            logging.error('Error occurred while trying to decode Stripe token response')
        except JSONDecodeError:
            exception_occurred = True
            logging.error('Could not convert token data into JSON object')
        except KeyError:
            exception_occurred = True
            logging.error('Access token missing in JSON object. Probably Stripe keys are configured improperly')
        except Exception:
            exception_occurred = True

        if exception_occurred:
            logging.error(traceback.format_exc())
            raise StripeRecipientsControllerException()

    def is_recipient_verified(self):
        if settings.ENVIRONMENT == Environments.DEV:
            return True
        else:
            recipient = stripe.Recipient.retrieve(self.stripe_recipient.recipient_id, settings.STRIPE_SECRET_KEY)
            return recipient.get('verified', False)

    def get_recipient_active_bank_account(self):
        if settings.ENVIRONMENT == Environments.DEV:
            account = {'id': 'fdjfhjdhfjhdjhfd', 'object': 'account'}
        else:
            recipient = stripe.Recipient.retrieve(self.stripe_recipient.recipient_id, settings.STRIPE_SECRET_KEY)
            logging.debug('%s' % recipient)
            account = recipient.get('active_account')
        logging.debug('%s' % account)
        return account

    def get_recipient_registered_cards(self):
        recipient = stripe.Recipient.retrieve(self.stripe_recipient.recipient_id, settings.STRIPE_SECRET_KEY)
        return {
            'cards': recipient['cards']['data'],
            'default_card_id': recipient['cards'].get('default_card')}

    def accept_payment(self, payment_description, card_token, amount):
        customer, error = create_customer(card_token, payment_description)

        if error:
            logging.error('Error during customer creation')
            logging.error(error)
            return {'success': False}

        token, error = create_token(customer, self.stripe_user.access_token)
        if error:
            logging.error('Error during token creation')
            logging.error(error)
            return {'success': False}

        charge, error = make_charge(amount, token, payment_description, self.stripe_user.access_token)
        if error:
            logging.error('Error during making charge')
            logging.error(error)
            return {'success': False}

        return {'success': True, 'charge_id': charge['id']}