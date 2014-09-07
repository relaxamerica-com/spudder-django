from django.contrib.auth.models import User
from django.db import models


class AmazonActionStatus():
    def __init__(self):
        pass

    SUCCESS = 'Success'
    A = 'A'
    CE = 'CE'
    NP = 'NP'
    NM = 'NM'
    SE = 'SE'
    PE = 'PE'
    SPUDDER_SAVE_FAILED = 'SPUDDER_SAVE_FAILED'

    @staticmethod
    def get_from_code(status_code):
        # status codes from https://amazonpayments.s3.amazonaws.com/FPS_ASP_Guides/FPS_Marketplace_Quick_Start.pdf
        if status_code == 'A':
            return AmazonActionStatus.A
        if status_code == 'CE':
            return AmazonActionStatus.CE
        if status_code == 'NP':
            return AmazonActionStatus.NP
        if status_code == 'NM':
            return AmazonActionStatus.NM
        if status_code == 'PE':
            return AmazonActionStatus.PE
        if status_code == 'SR': # Success for Recipient registration
            return AmazonActionStatus.SUCCESS
        if status_code == 'SA': # Success for ABT payment
            return AmazonActionStatus.SUCCESS
        if status_code == 'SB': # Success for ACH (bank account) payment
            return AmazonActionStatus.SUCCESS
        if status_code == 'SC': # Success for credit card payment
            return AmazonActionStatus.SUCCESS
        

    @staticmethod
    def get_status_message(status):
        if AmazonActionStatus.A == status:
            return 'Pipeline has been aborted by the user.'
        if AmazonActionStatus.CE == status:
            return 'Caller exception'
        if AmazonActionStatus.NP == status:
            return 'Pipeline problem'
        if AmazonActionStatus.NM == status:
            return 'You are not registered as a third-party caller to make this transaction. Contact Amazon Payments for more information.'
        if AmazonActionStatus.PE == status:
            return 'Payment Method Mismatch Error'
        if AmazonActionStatus.SPUDDER_SAVE_FAILED == status:
            return 'Error while saving information on Spudder. Please try again.'
        if AmazonActionStatus.SE == status:
            return 'System error'

        return 'Success'


class IPNTransactionStatus():
    def __init__(self):
        pass

    CANCELLED = 'CANCELLED'
    FAILURE = 'FAILURE'
    PENDING = 'PENDING'
    RESERVED = 'RESERVED'
    SUCCESS = 'SUCCESS'


class RecipientVerificationStatus():
    def __init__(self):
        pass

    PENDING = 'VerificationPending'
    COMPLETE = 'VerificationComplete'


class TransactionProgressStatus(models.Model):
    operation = models.CharField(max_length=255, default='')
    transactionDate = models.DateTimeField()
    notificationType = models.CharField(max_length=255, default='')
    certificateUrl = models.CharField(max_length=255, default='')
    recipientEmail = models.CharField(max_length=255, default='')
    signatureMethod = models.CharField(max_length=255, default='')
    signatureVersion = models.CharField(max_length=255, default='')
    callerReference = models.CharField(max_length=255, default='')
    buyerName = models.CharField(max_length=255, default='')
    signature = models.CharField(max_length=255, default='')
    recipientName = models.CharField(max_length=255, default='')
    transactionId = models.CharField(max_length=255, default='')
    transactionStatus = models.CharField(max_length=255, default='')
    paymentMethod = models.CharField(max_length=255, default='')
    transactionAmount = models.CharField(max_length=255, default='')
    statusMessage = models.CharField(max_length=255, default='')
    statusCode = models.CharField(max_length=255, default='')

    transaction_type = models.CharField(max_length=255, default='')
    transaction_entity_id = models.CharField(max_length=255, default='')
    transaction_user = models.ForeignKey(User, null=True, blank=True)