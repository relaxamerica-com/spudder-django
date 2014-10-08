import logging
import stripe
import httplib
import json
import urllib
from django.conf import settings
from settings import Environments



class StripeRecipientsController(object):
    def __init__(self, stripe_recipient, stripe_user):
        self.stripe_recipient = stripe_recipient
        self.stripe_user = stripe_user
        self._update_access_token()

    def _update_access_token(self):
        params = urllib.urlencode({
            'client_secret': settings.STRIPE_SECRET_KEY,
            'refresh_token': self.stripe_user.refresh_token,
            'grant_type': 'refresh_token'})
        url = '/oauth/token?%s' % params
        connection = httplib.HTTPSConnection('connect.stripe.com')
        connection.connect()
        connection.request('POST', url)
        resp = connection.getresponse()
        resp_data = resp.read()
        json_data = json.loads(resp_data)
        self.stripe_user.access_token = json_data['access_token']
        self.stripe_user.save()

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
        customer = stripe.Customer.create(
            card=card_token,
            description=payment_description,
            api_key=settings.STRIPE_SECRET_KEY)
        customer_id = customer['id']
        token = stripe.Token.create(
            customer=customer_id,
            api_key=self.stripe_user.access_token)
        token_id = token['id']
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                card=token_id,
                description=payment_description,
                api_key=self.stripe_user.access_token)
            return True
        except Exception as ex:
            logging.error("%s" % ex)
        return False
