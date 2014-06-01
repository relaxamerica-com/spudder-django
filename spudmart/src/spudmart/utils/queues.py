from google.appengine.api import taskqueue
import logging


def trigger_backend_task(url, target='payments', name=None, eta = None):
    logging.error('Executing new backend task')
    logging.error('URL: %s' % url)
    logging.error('Target: %s' % target)
    taskqueue.add(url=url, target=target, name=name, eta=eta)