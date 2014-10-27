import logging
from spudderstripe.api_utils import create_customer, create_token, make_charge
from spudderstripe.api_utils import get_account_details as _get_account_details


class StripeController(object):
    def __init__(self, stripe_user):
        self.stripe_user = stripe_user

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

    def get_account_details(self):
        account_details, error = _get_account_details(self.stripe_user.access_token)
        if error:
            logging.error('Error during get account details')
            logging.error(error)
            return None
        return account_details