import os
import traceback


def get_application_version():
    try:
        # CURRENT_VERSION_ID has <version>.<random_number> format
        version = os.environ['CURRENT_VERSION_ID'].split('.')[0]
    except Exception:
        version = 'spudmart'

    return version