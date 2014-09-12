from django.conf import settings


def amazon_client_id(_):
    return {'AMAZON_CLIENT_ID': settings.AMAZON_LOGIN_CLIENT_ID}