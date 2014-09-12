from django.http import HttpResponse
from django.conf import settings
import logging


def start(_):
    logging.error('Startup of backend....')
    return HttpResponse('Startup done', content_type='text/plain; charset=%s' % settings.DEFAULT_CHARSET)