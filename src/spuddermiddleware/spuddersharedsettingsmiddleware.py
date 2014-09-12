from django.conf import settings


class EnsureSharedSettingsMiddleware:
    if not settings.KROWDIO_CLIENT_KEY:
        raise Exception(
            "Krowd.io has not been configured for this environment, ensure there is a Krowd.io application or this "
            "instance and enter the KROWDIO_CLIENT_KEY in the appropriate shared_settings dictionary")
