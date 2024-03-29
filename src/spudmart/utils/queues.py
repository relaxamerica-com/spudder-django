from google.appengine.api import taskqueue
import logging


def trigger_backend_task(url, target='payments', name=None, eta=None):
    logging.info('Executing new backend task')
    logging.info('URL: %s' % url)
    logging.info('Target: %s' % target)
    taskqueue.add(url=url, target=target, name=name, eta=eta)