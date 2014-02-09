module.exports = function (keys) {
    return {
        recipient: function (req, res) {
            var amazonFPS = require('cloud/amazon/fps')(keys),
                teamID = req.params.teamID,
                params = {
                    'pipelineName': 'Recipient',
                    'recipientPaysFee': 'True',
                    'returnURL': 'https://' + keys.getAppName() + '.parseapp.com/dashboard/recipient/' + teamID + '/complete'
                };

            res.render('dashboard/sponsors/recipient', {
                'breadcrumbs' : [
                    { 'title' : 'Teams', 'href' : '/dashboard/teams' },
                    { 'title' : 'Registering as Recipient', 'href' : 'javascript:void(0);' }
                ],
                'cbui': amazonFPS.getCBUI(params)
            });
        },

        recipient_complete: function (req, res) {
            var tokenID = req.query.tokenID,
                refundTokenID = req.query.refundTokenID,
                signature = req.query.signature,
                callerReference = req.query.callerReference,
                teamID = req.params.teamID;

            var Team = Parse.Object.extend("Team"),
                query = new Parse.Query(Team);

            query.get(teamID).then(function (team) {
                var Recipient = Parse.Object.extend('Recipient'),
                    recipient = new Recipient();

                recipient.set('tokenID', tokenID);
                recipient.set('refundTokenID', refundTokenID);
                recipient.set('callerReference', callerReference);
                recipient.set('signature', signature);
                recipient.set('team', team);

                recipient.save(null, {
                    success: function () {
                        res.render('dashboard/sponsors/recipient_complete', {
                            'breadcrumbs' : [
                                { 'title' : 'Teams', 'href' : '/dashboard/teams' },
                                { 'title' : 'Registration complete', 'href' : 'javascript:void(0);' }
                            ],
                            'teamID': teamID,
                            'isError': false
                        });
                    },
                    error: function (recipient, error) {
                        res.render('dashboard/sponsors/recipient_complete', {
                            'breadcrumbs' : [
                                { 'title' : 'Teams', 'href' : '/dashboard/teams' },
                                { 'title' : 'Errors during registration', 'href' : 'javascript:void(0);' }
                            ],
                            'teamID': teamID,
                            'isError': true,
                            'error': error
                        });
                    }
                });
            });
        }
    }
};