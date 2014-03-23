from boto.fps.connection import FPSConnection
import settings


def _get_fps_connection():
    # Disabled SSL certificate verification due to GAE problems with Boto and SSL library
    # Reference: https://groups.google.com/forum/#!topic/boto-users/lzOKsZFKTM8
    return FPSConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_KEY_ID, validate_certs=False)


def get_recipient_cbui_url(team_id):
    connection = _get_fps_connection()

    return connection.cbui_url(returnURL='%s/dashboard/recipient/%s/complete' % (settings.SPUDMART_BASE_URL, team_id),
                               pipelineName='Recipient',
                               recipientPaysFee=True)


def get_donation_cbui_url(donation):
    connection = _get_fps_connection()
    return connection.cbui_url(returnURL='%s/dashboard/donation/%s/complete' % (settings.SPUDMART_BASE_URL, donation.id),
                               pipelineName='SingleUse',
                               transactionAmount=donation.donation,
                               paymentReason='Sponsoring %s' % donation.offer.team.name)