import datetime
from spudmart.amazon.utils import parse_ipn_notification_request
from nose_plugins.noseplugins import FormattedOutputTestCase
from nose.plugins.attrib import attr


class MockedRequest():
    def __init__(self):
        pass


class IPNNotificationParsing(FormattedOutputTestCase):
    @attr('unit')
    def test_parse_ipn_notification_request(self):
        request_mock = MockedRequest()
        request_mock.POST = {
            'operation': 'PAY',
            'transactionDate': '1402841022',
            'notificationType': 'TransactionStatus',
            'certificateUrl': 'https://fps.sandbox.amazonaws.com/certs/110713/PKICert.pem?requestId=15n5tlqv8hc05gibjv6xxu82cyev9lxqdzc4d2y5801qfcl',
            'recipientEmail': 'lukasz@spudder.com',
            'signatureMethod': 'RSA-SHA1',
            'signatureVersion': '2',
            'callerReference': '5b220133-7c1c-491c-b31a-f53768215158',
            'buyerName': 'Test Business',
            'signature': 'n78E5YHKt+dzq+WSTZ9y0Sox1UCTz+02tlUjco7VdamZEtPCdctLC7InWHCiL9ECtu7BswF+EquU\nruKpbg9pjtuYFz5MGPejTLvQW8hJBPSee7qoQMmZt8AevgJ2OEIQC2GGd9wTIgsrNBJRJ686qTQY\nEq5TaZTDwgGebSjKgBwiUYbTcUmn+mxnTQ+J/5dqSVviYlms6RxhlVPjkIuLsVCX1aouFsNCnapo\nnggyUmu9hcNPGermFZjzcOLJfMcltmVHe40puhUyj2DCpCuywehbBICP1uf6e9tp/hNFZW2hlLS2\n7te5HRJukoju9hiSs6dkQeu8RaAW9FZyDCh1mw==',
            'recipientName': 'Test Business',
            'transactionId': '214Z2841Z228Z34FJCTDO4CKE2AAUJVNI5L',
            'transactionStatus': 'SUCCESS',
            'paymentMethod': 'ABT',
            'transactionAmount': 'USD 10.00',
            'statusMessage': 'The transaction was successful and the payment instrument was charged.',
            'statusCode': 'Success'
        }

        progress_status = parse_ipn_notification_request(request_mock)

        self.assertEquals(progress_status.operation, 'PAY')
        self.assertEquals(progress_status.transactionDate, datetime.datetime.fromtimestamp(1402841022))
        self.assertEquals(progress_status.notificationType, 'TransactionStatus')
        self.assertEquals(progress_status.recipientEmail, 'lukasz@spudder.com')
        self.assertEquals(progress_status.signatureMethod, 'RSA-SHA1')
        self.assertEquals(progress_status.signatureVersion, '2')
        self.assertEquals(progress_status.callerReference, '5b220133-7c1c-491c-b31a-f53768215158')
        self.assertEquals(progress_status.buyerName, 'Test Business')
        self.assertEquals(progress_status.recipientName, 'Test Business')
        self.assertEquals(progress_status.transactionId, '214Z2841Z228Z34FJCTDO4CKE2AAUJVNI5L')
        self.assertEquals(progress_status.transactionStatus, 'SUCCESS')
        self.assertEquals(progress_status.paymentMethod, 'ABT')
        self.assertEquals(progress_status.transactionAmount, 'USD 10.00')
        self.assertEquals(progress_status.statusMessage, 'The transaction was successful and the payment instrument was charged.')
        self.assertEquals(progress_status.statusCode, 'Success')

        self.assertEquals(progress_status.transaction_type, '')
        self.assertEquals(progress_status.transaction_entity_id, '')
        self.assertIsNone(progress_status.transaction_user)
