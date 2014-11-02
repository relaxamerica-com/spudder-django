from nose.plugins.attrib import attr
from nose_plugins.noseplugins import FormattedOutputTestCase
from spudderstripe.utils import get_oauth_request_error, StripeOAuthError


class OAuthError(FormattedOutputTestCase):
    @attr('unit')
    def test_no_errors(self):
        request = type('', (), dict(GET={}))()

        error = get_oauth_request_error(request)

        self.assertIsNone(error)

    @attr('unit')
    def test_access_denied_error(self):
        request = type('', (), dict(GET={'error': 'access_denied'}))()

        error = get_oauth_request_error(request)

        self.assertIsNotNone(error)
        self.assertEquals(error, StripeOAuthError.ACCESS_DENIED)

    @attr('unit')
    def test_not_handled_error(self):
        request = type('', (), dict(GET={'error': 'unsupported_response_type'}))()

        error = get_oauth_request_error(request)

        self.assertIsNone(error)