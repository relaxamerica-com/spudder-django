module.exports = function (keys) {
    var amazonFPS = require('cloud/amazon/fps')(keys),
        amazonHelpers = require('cloud/amazon/helpers')();

    return {
        register: function (req, res) {
            var teamID = req.params.teamID,
                offerID = req.params.offerID,
                recipient, team, offer;

            var Team = Parse.Object.extend('Team'),
                teamQuery = new Parse.Query(Team);

            teamQuery.get(teamID).then(function(_team) {
                var Recipient = Parse.Object.extend('Recipient'),
                    recipientQuery = new Parse.Query(Recipient);

                recipientQuery.equalTo('team', _team);
                team = _team;

                return recipientQuery.find();
            }).then(function (recipients) {
                var TeamOffer = Parse.Object.extend('TeamOffer'),
                    teamOfferQuery = new Parse.Query(TeamOffer);

                recipient = recipients[0];

                return teamOfferQuery.get(offerID);
            }).then(function(_offer) {
                offer = _offer;

                return Parse.User.current().fetch();
            }).then(function (user) {
                var refundTokenID = recipient.get('refundTokenID'),
                    teamName = team.get('name'),
                    amount = offer.get('donation'),
                    returnURL = 'https://' + keys.getAppName() + '.parseapp.com/dashboard/payments/donate/complete';

                returnURL += '?teamID=' + encodeURIComponent(teamID);
                returnURL += '&offerID=' + encodeURIComponent(offerID);
                returnURL += '&refundTokenID=' + encodeURIComponent(refundTokenID);
                returnURL += '&sponsorID=' + encodeURIComponent(user.id);

                var params = {
                    'pipelineName': 'SingleUse',
                    'transactionAmount': '' + amount,
                    'paymentReason': 'Sponsoring ' + teamName + ' - offer ' + offer.get('title'),
                    'returnURL': returnURL
                };

                res.render('dashboard/payments/donate/register', {
                    'breadcrumbs' : [
                        { 'title' : 'Sponsors', 'href' : '/dashboard/sponsor' },
                        { 'title' : 'Confirm donation', 'href' : 'javascript:void(0);' }
                    ],
                    'cbui': amazonFPS.getCBUI(params),
                    'team': team,
                    'offer': offer
                });
            });
        },

        register_complete: function (req, res) {
            var query = req.query,
                tokenID = query.tokenID,
                signature = query.signature,
                callerReference = query.callerReference,
                teamID = query.teamID,
                offerID = query.offerID,
                sponsorID = query.sponsorID,
                status = query.status,
                refundTokenID = query.refundTokenID,
                statusInfo = amazonHelpers.getStatusInfo(status);

            if (statusInfo.isError) {
                res.redirect('/dashboard/payments/donate/thanks?error=' + encodeURIComponent(statusInfo.errorMessage));
                return;
            }

            var Team = Parse.Object.extend("Team"),
                teamQuery = new Parse.Query(Team),
                team, offer;

            teamQuery.get(teamID).then(function(_team) {
                team = _team;

                return (new Parse.Query(Parse.Object.extend('TeamOffer'))).get(offerID);
            }).then(function(_offer) {
                offer = _offer;

                return (new Parse.Query(Parse.User)).get(sponsorID);
            }).then(function(sponsor) {
                var Donation = Parse.Object.extend('Donation'),
                    donation = new Donation();

                donation.set('tokenID', tokenID);
                donation.set('callerReference', callerReference);
                donation.set('signature', signature);
                donation.set('refundTokenID', refundTokenID);
                donation.set('offer', offer);
                donation.set('team', team);
                donation.set('sponsor', sponsor);

                donation.save(null, {
                    success: function () {
                        var roleACL = new Parse.ACL(),
                            teamAdminRole = new Parse.Role("Sponsor", roleACL);

                        roleACL.setPublicReadAccess(true);

                        teamAdminRole.getUsers().add(sponsor);
                        teamAdminRole.save();

                        res.redirect('/dashboard/payments/donate/thanks');
                    },
                    error: function (recipient, error) {
                        res.redirect('/dashboard/payments/donate/thanks?error=' + encodeURIComponent(error));
                    }
                });
            });
        },

        register_thanks: function (req, res) {
            Parse.User.current().fetch().then(function (sponsor) {
                var SponsorPage = Parse.Object.extend('SponsorPage'),
                    sponsorPageQuery = new Parse.Query(SponsorPage);

                sponsorPageQuery.equalTo('sponsor', sponsor);

                sponsorPageQuery.find().then(function (results) {
                    res.render('dashboard/payments/donate/register_thanks', {
                        'breadcrumbs' : [
                            { 'title' : 'Sponsors', 'href' : '/dashboard/sponsor' },
                            { 'title' : 'Donation complete', 'href' : 'javascript:void(0);' }
                        ],
                        'sponsorPageExists': results.length > 0
                    });
                });
            });
        },

        register_error: function (req, res) {
            res.render('dashboard/payments/donate/register_error', {
                'breadcrumbs' : [
                    { 'title' : 'Sponsors', 'href' : '/dashboard/sponsor' },
                    { 'title' : 'Errors during donation process', 'href' : 'javascript:void(0);' }
                ],
                'error': req.query.error
            });
        }
    }
};