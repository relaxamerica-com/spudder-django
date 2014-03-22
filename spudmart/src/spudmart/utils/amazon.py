from boto.fps.connection import FPSConnection
import settings


def _get_fps_connection():
    # Disabled SSL certificate verification due to GAE problems with Boto and SSL library
    # Reference: https://groups.google.com/forum/#!topic/boto-users/lzOKsZFKTM8
    return FPSConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_KEY_ID, validate_certs=False)