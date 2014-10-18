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


class StripeRecipientsController(object):
    def __init__(self, stripe_recipient, stripe_user):
        self.stripe_recipient = stripe_recipient
        self.stripe_user = stripe_user

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