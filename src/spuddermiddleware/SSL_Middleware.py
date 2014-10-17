import re

__license__ = "Python"
__copyright__ = "Copyright (C) 2007, Stephen Zabel"
__author__ = "Stephen Zabel - sjzabel@gmail.com"
__contributors__ = "Jay Parlar - parlar@gmail.com"

from django.conf import settings
from django.http import HttpResponsePermanentRedirect, get_host

SSL = 'SSL'
SKIPPED_URLS = re.compile('(^/file.*|^/venues/rent_venue/\d+/notification/\d+|^/venues/rent_venue/sign_in_complete|^/stripe.*|)')


class SSLRedirect:
    def __init__(self):
        pass

    def process_view(self, request, view_func, view_args, view_kwargs):
        # We need to pop the potential args and kwargs even if we are skipping this processing. MG: 20140623
        secure = view_kwargs.pop(SSL, False)
        secure_unauthenticated = view_kwargs.pop('SSL_unauthenticated', False)

        if SKIPPED_URLS.match(request.path) or request.META['SERVER_NAME'] in ['localhost', 'testserver']:
            return None

        if not secure and secure_unauthenticated and not request.user.is_authenticated():
            secure = True

        if not secure == self._is_secure(request):
            return self._redirect(request, secure)

    def _is_secure(self, request):
        if request.is_secure():
            return True

        #Handle the Webfaction case until this gets resolved in the request.is_secure()
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        return False

    def _redirect(self, request, secure):
        protocol = secure and "https" or "http"
        newurl = "%s://%s%s" % (protocol,get_host(request),request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError, \
        """Django can't perform a SSL redirect while maintaining POST data.
           Please structure your views so that redirects only occur during GETs."""

        return HttpResponsePermanentRedirect(newurl)