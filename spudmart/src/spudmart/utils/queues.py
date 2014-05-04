from google.appengine.api import taskqueue
from spudmart.utils.app_identity import get_application_version
import logging


def trigger_backend_task(url, target='payments' + get_application_version(), name=None, eta = None):
    logging.error('Executing new backend task')
    logging.error('URL: %s' % url)
    logging.error('Target: %s' % target)
    taskqueue.add(url=url, target=target, name=name, eta=eta)