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
        },

        sponsor: function (req, res) {
            var teamID = req.params.teamID,
                offerID = req.params.offerID,
                recipient;

            var Team = Parse.Object.extend('Team'),
                teamQuery = new Parse.Query(Team);

            teamQuery.get(teamID, {
                success: function(team) {
                    var Recipient = Parse.Object.extend('Recipient'),
                        query = new Parse.Query(Recipient);

                    query.equalTo('team', team);

                    query.find({
                        success: function (results) {
                            recipient = results[0];

                            var TeamOffer = Parse.Object.extend('TeamOffer'),
                                offerQuery = new Parse.Query(TeamOffer);

                            offerQuery.get(offerID,{
                                success: function(offer) {
                                    Parse.User.current().fetch().then(function (user) {
                                        var refundTokenID = recipient.get('refundTokenID'),
                                            teamName = team.get('name'),
                                            amount = offer.get('donation'),
                                            returnURL = 'https://' + keys.getAppName() + '.parseapp.com/dashboard/sponsor/complete';

                                        returnURL += '?teamID=' + encodeURIComponent(teamID);
                                        returnURL += '&offerID=' + encodeURIComponent(offerID);
                                        returnURL += '&refundTokenID=' + encodeURIComponent(refundTokenID);
                                        returnURL += '&sponsorID=' + encodeURIComponent(user.id);

                                        var amazonFPS = require('cloud/amazon/fps')(keys),
                                            params = {
                                                'pipelineName': 'SingleUse',
                                                'transactionAmount': '' + amount,
                                                'paymentReason': 'Sponsoring ' + teamName + ' - offer ' + offer.get('title'),
                                                'returnURL': returnURL
                                            };

                                        res.render('dashboard/sponsors/sponsor', {
                                            'breadcrumbs' : [
                                                { 'title' : 'Sponsors', 'href' : '/dashboard/sponsor' },
                                                { 'title' : 'Confirm donation', 'href' : 'javascript:void(0);' }
                                            ],
                                            'cbui': amazonFPS.getCBUI(params),
                                            'team': team,
                                            'offer': offer
                                        });
                                    });

                                }
                            });
                        }
                    });
                }
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
                    'breadcrumbs' : [
                        { 'title' : 'Sponsors', 'href' : '/dashboard/sponsor' },
                        { 'title' : 'Donation completed with errors', 'href' : 'javascript:void(0);' }
                    ],
                    'isError': true,
                    'error': errorMsg
                });
            }

            var query = req.query,
                tokenID = query.tokenID,
                signature = query.signature,
                callerReference = query.callerReference,
                teamID = query.teamID,
                offerID = query.offerID,
                sponsorID = query.sponsorID,
                status = query.status,
                refundTokenID = query.refundTokenID,
                isError = false, errorMessage = '';

            checkStatus();

            if (isError) {
                renderError(errorMessage);
            } else {
                var Team = Parse.Object.extend("Team"),
                    teamQuery = new Parse.Query(Team);

                teamQuery.get(teamID, {
                    success: function(team) {
                        var TeamOffer = Parse.Object.extend('TeamOffer'),
                            offerQuery = new Parse.Query(TeamOffer);

                        offerQuery.get(offerID,{
                            success: function(offer) {
                                var userQuery = new Parse.Query(Parse.User);
                                userQuery.get(sponsorID, {
                                    success: function(sponsor) {
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
                                                var roleACL = new Parse.ACL();
                                                roleACL.setPublicReadAccess(true);
                                                var teamAdminRole = new Parse.Role("Sponsor", roleACL);
                                                teamAdminRole.getUsers().add(sponsor);
                                                teamAdminRole.save();

                                                res.render('dashboard/sponsors/sponsor_complete', {
                                                    'breadcrumbs' : [
                                                        { 'title' : 'Sponsors', 'href' : '/dashboard/sponsor' },
                                                        { 'title' : 'Donation complete', 'href' : 'javascript:void(0);' }
                                                    ],
                                                    'isError': false
                                                });
                                            },
                                            error: function (recipient, error) {
                                                renderError(error);
                                            }
                                        });

                                    }
                                });
                            },
                            error: function(object, error) {
                                console.log('Error fetching Offer (' + offerID + ')');
                                console.log(error);
                                res.render('teams/offer/error');
                            }
                        });
                    },
                    error: function(object, error) {
                        console.log('Error fetching Team (' + teamID + ')');
                        console.log(error);
                        res.render('teams/offer/error');
                    }
                });
            }
        },

        donations: function (req, res) {
            var _ = require('underscore');

            Parse.User.current().fetch().then(function (user) {
                var Donation = Parse.Object.extend('Donation'),
                    query = new Parse.Query(Donation),
                    donations = [], totalAmount = 0;

                query.equalTo('sponsor', user);

                query.find().then(function (list) {
                    var promise = Parse.Promise.as();

                    _.each(list, function(donation) {
                        promise = promise.then(function() {
                            var findPromise = new Parse.Promise();

                            var offer = donation.get('offer'),
                                team = donation.get('team');

                            offer.fetch({
                                success: function (fetchedOffer) {
                                    team.fetch({
                                        success: function (fetchedTeam) {
                                            donations.push({
                                                tokenID: donation.get('tokenID'),
                                                offer: fetchedOffer,
                                                team: fetchedTeam
                                            });

                                            totalAmount += parseFloat(fetchedOffer.get('donation'));

                                            findPromise.resolve();
                                        }
                                    });
                                }
                            });

                            return findPromise;
                        });
                    });

                    return promise;
                }).then(function () {
                    res.render('dashboard/sponsors/donations', {
                        'breadcrumbs' : [
                            { 'title' : 'Sponsors', 'href' : '/dashboard/sponsor' },
                            { 'title' : 'My donations', 'href' : 'javascript:void(0);' }
                        ],
                        'donations': donations,
                        'totalAmount': totalAmount
                    });
                });
            });
        }
    };
};