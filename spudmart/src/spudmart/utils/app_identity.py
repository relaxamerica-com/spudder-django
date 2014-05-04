import os
import traceback


def get_application_version():
    try:
        # CURRENT_VERSION_ID has <version>.<random_number> format
        version = os.environ['CURRENT_VERSION_ID']
        if version.find('.') != -1:  # function called in frontend
            version = version.split('.')[0]
    except Exception:
        version = 'spudmart'

    return version