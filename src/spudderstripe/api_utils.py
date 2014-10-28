import settings
import stripe


def make_api_call(api_method, args):
    """
    Uses Stripe API Python bindings (from official library) and handles any errors and exceptions that can happen

    :param api_method:
    :param args: arguments passed to api_method
    :return: (stripe_object, error_object) - stripe_stripe_object represents returned value from api_method,
            error_object describes what happen wrong (at least it has error_type, other fields available only
            for CardError)
    """

    stripe_object = None
    error_object = None

    try:
        stripe_object = api_method(*args)
    except stripe.error.CardError, e:
        error_object = {
            'error_type': stripe.error.CardError
        }

        if not hasattr(e, 'json_body') or 'error' not in e.json_body:
            pass

        stripe_error = e.json_body['error']
        if 'type' in stripe_error:
            error_object['type'] = stripe_error['type']
        if 'code' in stripe_error:
            error_object['code'] = stripe_error['code']
        if 'param' in stripe_error:
            error_object['param'] = stripe_error['param']
        if 'message' in stripe_error:
            error_object['message'] = stripe_error['message']
    except stripe.error.InvalidRequestError, e:
        # Invalid parameters were supplied to Stripe's API

        error_object = {'error_type': stripe.error.InvalidRequestError}
    except stripe.error.AuthenticationError, e:
        # Authentication with Stripe's API failed

        error_object = {'error_type': stripe.error.AuthenticationError}
    except stripe.error.APIConnectionError, e:
        # Network communication with Stripe failed

        error_object = {'error_type': stripe.error.APIConnectionError}
    except stripe.error.StripeError, e:
        # Temporary and generic error from Stripe API, doesn't tells us what actually happened

        error_object = {'error_type': stripe.error.StripeError}
    except Exception, e:
        # Something else happened, completely unrelated to Stripe

        error_object = {'error_type': Exception, 'error': '%s' % e}

    return stripe_object, error_object


def create_customer(customer_card_token, customer_payment_description):
    def logic(card_token, payment_description):
        customer = stripe.Customer.create(
            card=card_token,
            description=payment_description,
            api_key=settings.STRIPE_SECRET_KEY)

        return customer

    return make_api_call(logic, (customer_card_token, customer_payment_description))


def create_token(token_customer, token_api_key):
    def logic(customer, api_key):
        token = stripe.Token.create(
            customer=customer['id'],
            api_key=api_key)

        return token

    return make_api_call(logic, (token_customer, token_api_key))


def make_charge(charge_amount, charge_token, charge_payment_description, charge_api_key):
    def logic(amount, token, payment_description, api_key):
        created_charge = stripe.Charge.create(
            amount=amount,
            currency="usd",
            card=token['id'],
            description=payment_description,
            api_key=api_key)

        return created_charge

    return make_api_call(logic, (charge_amount, charge_token, charge_payment_description, charge_api_key))


def get_account_details(account_access_token):
    if settings.ENVIRONMENT in [settings.Environments.DEV]:
        return {'display_name': 'Business in Development'}, None

    def logic(api_key):
        account_details = stripe.Account.retrieve(api_key)
        return account_details

    return make_api_call(logic, (account_access_token, ))