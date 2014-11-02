from nose.plugins.attrib import attr
from nose_plugins.noseplugins import FormattedOutputTestCase
from minimock import Mock
import spudderstripe.api_utils
from spudderstripe.controllers import StripeController
import stripe


class StubbedStripeUser():
    def __init__(self):
        self.access_token = '12345679'


class PaymentAcceptance(FormattedOutputTestCase):
    def setUp(self):
        self.stripe_controller = StripeController(StubbedStripeUser())

        spudderstripe.api_utils.create_customer = Mock('Mocked_api_utils_create_customer')
        spudderstripe.api_utils.create_customer.mock_returns = (None, None)

        spudderstripe.api_utils.create_token = Mock('Mocked_api_utils_create_token')
        spudderstripe.api_utils.create_token.mock_returns = (None, None)

        spudderstripe.api_utils.make_charge = Mock('Mocked_api_utils_make_charge')
        spudderstripe.api_utils.make_charge.mock_returns = ({'id': 999}, None)


    @attr('unit')
    def test_payment_accepted(self):
        result = self.stripe_controller.accept_payment(payment_description='Some description',
                                                       card_token='456465156', amount=10)

        self.assertTrue(result['success'])
        self.assertEquals(result['charge_id'], 999)

    @attr('unit')
    def test_customer_creation_failed(self):
        spudderstripe.api_utils.create_customer.mock_returns = (None, stripe.error.StripeError())

        result = self.stripe_controller.accept_payment(payment_description='Some description',
                                                       card_token='456465156', amount=10)

        self.assertFalse(result['success'])
        self.assertFalse('charge_id' in result)

    @attr('unit')
    def test_token_creation_failed(self):
        spudderstripe.api_utils.create_token.mock_returns = (None, stripe.error.StripeError())

        result = self.stripe_controller.accept_payment(payment_description='Some description',
                                                       card_token='456465156', amount=10)

        self.assertFalse(result['success'])
        self.assertFalse('charge_id' in result)

    @attr('unit')
    def test_actual_charge_failed(self):
        spudderstripe.api_utils.make_charge.mock_returns = (None, stripe.error.StripeError())

        result = self.stripe_controller.accept_payment(payment_description='Some description',
                                                       card_token='456465156', amount=10)

        self.assertFalse(result['success'])
        self.assertFalse('charge_id' in result)