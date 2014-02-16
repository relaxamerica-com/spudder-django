module.exports = function (keys) {
    return {
        register: function (req, res) {
            var amazonFPS = require('cloud/amazon/fps')(keys),
                teamID = req.params.teamID,
                params = {
                    'pipelineName': 'Recipient',
                    'recipientPaysFee': 'True',
                    'returnURL': 'https://' + keys.getAppName() + '.parseapp.com/dashboard/payments/recipient/' + teamID + '/complete'
                };

            res.render('dashboard/payments/recipient/register', {
                'breadcrumbs' : [
                    { 'title' : 'Teams', 'href' : '/dashboard/teams' },
                    { 'title' : 'Registering as Recipient', 'href' : 'javascript:void(0);' }
                ],
                'cbui': amazonFPS.getCBUI(params)
            });
        },

        register_complete: function (req, res) {
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
                        res.redirect('/dashboard/payments/recipient/' + teamID + '/thanks');
                    },
                    error: function (recipient, error) {
                        res.redirect('/dashboard/payments/recipient/' + teamID + '/error?error=' + encodeURIComponent(error));
                    }
                });
            });
        },

        register_thanks: function (req, res) {
            var teamID = req.params.teamID;

            res.render('dashboard/payments/recipient/register_thanks', {
                'breadcrumbs' : [
                    { 'title' : 'Teams', 'href' : '/dashboard/teams' },
                    { 'title' : 'Registration complete', 'href' : 'javascript:void(0);' }
                ],
                'teamID': teamID
            });
        },

        register_error: function (req, res) {
            var teamID = req.params.teamID,
                error = req.query.error;

            res.render('dashboard/payments/recipient/register_error', {
                'breadcrumbs' : [
                    { 'title' : 'Teams', 'href' : '/dashboard/teams' },
                    { 'title' : 'Errors during registration', 'href' : 'javascript:void(0);' }
                ],
                'error': error
            });
        }
    }
};