from boto.fps.connection import FPSConnection
import settings
from spudmart.recipients.models import Recipient


def get_fps_connection():
    # Disabled SSL certificate verification due to GAE problems with Boto and SSL library
    # Reference: https://groups.google.com/forum/#!topic/boto-users/lzOKsZFKTM8
    return FPSConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_KEY_ID, validate_certs=False)


def get_recipient_cbui_url(team_id):
    connection = get_fps_connection()

    return connection.cbui_url(returnURL='%s/dashboard/recipient/%s/complete' % (settings.SPUDMART_BASE_URL, team_id),
                               pipelineName='Recipient',
                               recipientPaysFee=False, maxVariableFee='10')


def get_donation_cbui_url(donation):
    connection = get_fps_connection()
    
    team = donation.offer.team
    recipients = Recipient.objects.filter(team=team)
    recipientTokenId = recipients[0].recipient_token_id
    
    return connection.cbui_url(returnURL='%s/dashboard/donation/%s/complete' % (settings.SPUDMART_BASE_URL, donation.id),
                               pipelineName='MultiUse',
                               transactionAmount=donation.donation,
                               paymentReason='Sponsoring %s' % donation.offer.team.name,
                               globalAmountLimit=donation.donation,
                               isRecipientCobranding='True',
                               recipientTokenList=recipientTokenId,
                               amountType='Exact',
                               currencyCode='USD')