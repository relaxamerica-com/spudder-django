import os
import traceback
from google.appengine.api.app_identity import get_application_id


def get_spudmart_app_name():
    try:
        app_name = get_application_id()
    except Exception:
        app_name = 'spudmart1'

    return app_name