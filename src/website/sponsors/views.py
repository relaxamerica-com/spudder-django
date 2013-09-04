from django.shortcuts import render
from django.conf import settings
from boto.fps.connection import FPSConnection
from django.http import HttpResponseRedirect

def _get_fps_connection():
    # Disabled SSL certificate verification due to GAE problems with Boto and SSL library
    # Reference: https://groups.google.com/forum/#!topic/boto-users/lzOKsZFKTM8
    return FPSConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_KEY_ID, validate_certs=False)

def index(request):
    return render(request, 'sponsors/index.html')

def call_cbui(request):
    fps_connection = _get_fps_connection()
    
    transactionAmount = request.GET.get('transactionAmount')
    teamName = request.GET.get('teamName')
    
    from logging import info
    info('-'*60)
    info('Name: %s' % teamName)
    info('Amount: %s' % transactionAmount)

    cbui_url = fps_connection.cbui_url(returnURL='%s/sponsors/thanks' % settings.DOMAIN_NAME, pipelineName='SingleUse', transactionAmount=transactionAmount,
                                       paymentReason='Sponsoring %s' % teamName)
    
    return HttpResponseRedirect(cbui_url)

def thanks(request):
    tokenID = request.GET.get('tokenID')
    
    return render(request, 'sponsors/thank_you.html', {'tokenID': tokenID})

def register_recipient(request):
    fps_connection = _get_fps_connection()
    
    cbui_url = fps_connection.cbui_url(returnURL='%s/sponsors/thanks_recipient' % settings.DOMAIN_NAME, pipelineName='Recipient', recipientPaysFee=True)
    
    return render(request, 'sponsors/register.html', {'cbui_url': cbui_url})

def thanks_recipient(request):
    tokenID = request.GET.get('tokenID')
    refundTokenID = request.GET.get('refundTokenID')
    
    status_code = request.GET.get('status')
    status = 'Success'
    if status_code == 'A':
        status = 'Pipeline has been aborted by the user.'
    elif status_code == 'CE':
        status = 'Caller exception'
    elif status_code == 'NP':
        status = 'Pipeline problem'
    elif status_code == 'NM':
        status = 'You are not registered as a third-party caller to make this transaction. Contact Amazon Payments for more information.'
    
    return render(request, 'sponsors/thank_you_recipient.html', {'tokenID': tokenID, 'refundTokenID': refundTokenID, 'status': status})