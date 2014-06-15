import datetime
from boto.fps.connection import FPSConnection
import settings
from spudmart.amazon.models import TransactionProgressStatus
from spudmart.recipients.models import Recipient, VenueRecipient


def get_fps_connection():
    # Disabled SSL certificate verification due to GAE problems with Boto and SSL library
    # Reference: https://groups.google.com/forum/#!topic/boto-users/lzOKsZFKTM8
    return FPSConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_KEY_ID, validate_certs=False)

def _get_recipient_cbui_url(returnURL):
    connection = get_fps_connection()

    return connection.cbui_url(returnURL=returnURL,
                               pipelineName='Recipient',
                               recipientPaysFee=False, maxVariableFee='10')

def get_recipient_cbui_url(team_id):
    return _get_recipient_cbui_url('%s/dashboard/recipient/%s/complete' % (settings.SPUDMART_BASE_URL, team_id))


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
    
def get_venue_recipient_cbui_url(venue):
    return _get_recipient_cbui_url('%s/venues/recipient/%s/complete' % (settings.SPUDMART_BASE_URL, venue.id))

def get_rent_venue_cbui_url(venue):
    connection = get_fps_connection()
    
    recipients = VenueRecipient.objects.filter(groundskeeper = venue.user)
    recipientTokenId = recipients[0].recipient_token_id
    
    return connection.cbui_url(returnURL='%s/venues/rent_venue/%s/complete' % (settings.SPUDMART_BASE_URL, venue.id),
                               pipelineName='MultiUse',
                               transactionAmount=venue.price,
                               paymentReason='Renting Venue: %s' % venue.name,
                               globalAmountLimit=venue.price,
                               isRecipientCobranding='True',
                               recipientTokenList=recipientTokenId,
                               amountType='Exact',
                               currencyCode='USD')


def get_rent_venue_ipn_url(venue, user):
    return '%s/venues/rent_venue/%s/notification/%s' % (settings.SPUDMART_BASE_URL, venue.id, user.id)


def parse_ipn_notification_request(request):
    progress_status = TransactionProgressStatus()

    progress_status.transactionDate = datetime.datetime.fromtimestamp(long(request.POST['transactionDate']))

    for key, value in request.POST.iteritems():
        if not getattr(progress_status, key):
            setattr(progress_status, key, value)

    return progress_status