module.exports = function (keys) {
    return {
        spuds: function (req, res) {
            var breadcrumbs = ['SPUDS'];
            res.render('dashboard/spuds', {
                'breadcrumbs' : breadcrumbs
            });
        },

        general: function (req, res) {
            var breadcrumbs = ['Fans', 'General'];
            res.render('dashboard/fan/general', {
                'breadcrumbs' : breadcrumbs,
                'displayUsers' : require('cloud/commons/displayUsers'),
                'modalTop' : require('cloud/dashboard/fan/modalTop'),
                'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
            });
        },

        recipient: function (req, res) {
            var amazonFPS = require('cloud/amazon/fps')(keys),
                params = {
                    'pipelineName': 'Recipient',
                    'recipientPaysFee': 'True',
                    'returnURL': 'https://' + keys.getAppName() + '.parseapp.com/dashboard/recipient/complete'
            };

            res.render('dashboard/sponsors/recipient', {
                'breadcrumbs' : ['Sponsors', 'Became a recipient'],
                'cbui': amazonFPS.getCBUI(params)
            });
        },

        recipient_complete: function (req, res) {
            var query = req.query;

            res.render('dashboard/sponsors/recipient_complete', {
                'breadcrumbs' : ['Sponsors', 'Saving team in database'],
                'tokenID': query.tokenID,
                'refundTokenID': query.refundTokenID,
                'callerReference': query.callerReference,
                'signature': query.signature
            });
        },

        recipient_save: function (req, res) {
            var tokenID = req.body.tokenID,
                refundTokenID = req.body.refundTokenID,
                signature = req.body.signature,
                callerReference = req.body.callerReference,
                teamName = req.body.name;

            var Recipient = Parse.Object.extend('Recipient'),
                recipient = new Recipient();

            recipient.set('tokenID', tokenID);
            recipient.set('refundTokenID', refundTokenID);
            recipient.set('callerReference', callerReference);
            recipient.set('signature', signature);
            recipient.set('name', teamName);

            recipient.save(null, {
                success: function () {
                    res.render('dashboard/sponsors/recipient_save', {
                        'breadcrumbs': ['Sponsors', 'Registration complete'],
                        'isError': false
                    });
                },
                error: function (recipient, error) {
                    res.render('dashboard/sponsors/recipient_save', {
                        'breadcrumbs': ['Sponsors', 'Registration complete'],
                        'isError': true,
                        'error': error
                    });
                }
            });
        },

        sponsor: function (req, res) {
            var Recipient = Parse.Object.extend('Recipient'),
                query = new Parse.Query(Recipient),
                recipients = [], count, result, i;

            query.ascending('name');

            query.find({
                success: function (results) {
                    count = results.length;

                    for (i = 0; i < count; i++) {
                        result = results[i];

                        recipients.push({
                            'name': result.get('name'),
                            'refundTokenID': result.get('refundTokenID')
                        });
                    }

                    res.render('dashboard/sponsors/sponsor', {
                        'breadcrumbs': ['Sponsors', 'Became a sponsor'],
                        'recipients': recipients
                    });
                }
            });
        },

        sponsor_confirm: function (req, res) {
            var refundTokenID = req.body.refundTokenID,
                teamName = req.body.teamName,
                amount = parseFloat(req.body.amount),
                returnURL = 'https://' + keys.getAppName() + '.parseapp.com/dashboard/sponsor/complete';

            returnURL += '?refundTokenID=' + encodeURIComponent(refundTokenID);
            returnURL += '&amount=' + encodeURIComponent(amount);

            var amazonFPS = require('cloud/amazon/fps')(keys),
                params = {
                    'pipelineName': 'SingleUse',
                    'transactionAmount': '' + amount,
                    'paymentReason': 'Sponsoring ' + teamName,
                    'returnURL': returnURL
                };

            res.render('dashboard/sponsors/sponsor_confirm', {
                'breadcrumbs': ['Sponsors', 'Confirm donation'],
                'cbui': amazonFPS.getCBUI(params),
                'amount': '' + amount,
                'teamName': teamName
            });
        },

        sponsor_complete: function (req, res) {
            function checkStatus() {
                switch (status) {
                    case 'A':
                        isError = true;
                        errorMessage = 'Transaction has been aborted by the user.';
                        break;
                    case 'CE':
                        isError = true;
                        errorMessage = 'Caller exception';
                        break;
                    case 'NP':
                        isError = true;
                        errorMessage = 'Transaction problem';
                        break;
                    case 'NM':
                        isError = true;
                        errorMessage = 'You are not registered as a third-party caller to make this transaction. Contact Amazon Payments for more information.';
                        break;
                }
            }

            function renderError(errorMsg) {
                res.render('dashboard/sponsors/sponsor_complete', {
                    'breadcrumbs': ['Sponsors', 'Donation completed'],
                    'isError': true,
                    'error': errorMsg
                });
            }

            var query = req.query,
                tokenID = query.tokenID,
                signature = query.signature,
                callerReference = query.callerReference,
                refundTokenID = query.refundTokenID,
                status = query.status,
                amount = query.amount,
                isError = false, errorMessage = '';

            checkStatus();

            if (isError) {
                renderError(errorMessage);
            } else {
                var Recipient = Parse.Object.extend('Recipient'),
                    databaseQuery = new Parse.Query(Recipient),
                    recipients = [], count, result, i;

                databaseQuery.equalTo('refundTokenID', refundTokenID);

                databaseQuery.first({
                    success: function (recipient) {
                        var Donation = Parse.Object.extend('Donation'),
                            donation = new Donation();

                        donation.set('tokenID', tokenID);
                        donation.set('callerReference', callerReference);
                        donation.set('signature', signature);
                        donation.set('refundTokenID', refundTokenID);
                        donation.set('amount', amount);
                        donation.set('teamName', recipient.get('name'));

                        donation.save(null, {
                            success: function () {
                                res.render('dashboard/sponsors/sponsor_complete', {
                                    'breadcrumbs': ['Sponsors', 'Registration complete'],
                                    'isError': false
                                });
                            },
                            error: function (recipient, error) {
                                renderError(error);
                            }
                        });
                    }
                });
            }
        },

        list_donations: function (req, res) {
            var Donation = Parse.Object.extend('Donation'),
                query = new Parse.Query(Donation),
                donations = [], count, i, totalAmount = 0;

            query.descending('refundTokenID');

            query.find({
                success: function (results) {
                    count = results.length;

                    for (i = 0; i < count; i++) {
                        donations.push({
                            tokenID: results[i].get('tokenID'),
                            rank: '' + (i + 1),
                            amount: results[i].get('amount'),
                            teamName: results[i].get('teamName')
                        });

                        totalAmount += parseFloat(results[i].get('amount'));
                    }

                    res.render('dashboard/sponsors/donations', {
                        'breadcrumbs': ['Donations'],
                        'count': count,
                        'donations': donations,
                        'totalAmount': totalAmount
                    });
                }
            });
        }
    };
};