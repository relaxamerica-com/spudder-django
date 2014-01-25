module.exports = function (keys) {
    var helpers = require('cloud/teams/helpers')();
    var _ = require('underscore');

    return {
        list: function (req, res) {
            var Team = Parse.Object.extend("Team"),
                query = new Parse.Query(Team),
                teamID = req.params.teamID,
                offersCount = 0, teamAdmin;

            query.get(teamID, {
                success: function(team) {
                    var TeamOffer = Parse.Object.extend("TeamOffer"),
                        offerQuery = new Parse.Query(TeamOffer),
                        currentOffers = [],
                        currentDate = new Date(),
                        currentDateString = currentDate.getFullYear() + '-' +
                            ('0' + (currentDate.getMonth() + 1)).slice(-2) + '-' +
                            ('0' + currentDate.getDate()).slice(-2);

                    offerQuery.equalTo('team', team);

                    offerQuery.find().then(function (offers) {
                        offersCount = offers.length;
                        var promise = Parse.Promise.as();

                        _.each(offers, function(offer) {
                            var endDate = offer.get('endDate');

                            var endDateSplitted = endDate.split('-'),
                                year = endDateSplitted[0],
                                month = endDateSplitted[1],
                                day = endDateSplitted[2];

                            month = ('0' + month).slice(-2);
                            day = ('0' + day).slice(-2);
                            endDate = year + '-' + month + '-' + day;

                            // Database end date format is YYYY-MM-DD, user format is DD-MM-YYYY
                            var revertedEndDate = helpers.revertDate(offer.get('endDate'));
                            offer.set('endDate', revertedEndDate);

                            promise = promise.then(function() {
                                var findPromise = new Parse.Promise(),
                                    Donation = Parse.Object.extend('Donation'),
                                    donationQuery = new Parse.Query(Donation);

                                donationQuery.equalTo('offer', offer);

                                donationQuery.find().then(function (donations) {
                                    offer.set('available', offer.get('quantity') - donations.length);

                                    if (endDate >= currentDateString) {
                                        currentOffers.push(offer);
                                    }

                                    findPromise.resolve();
                                });

                                return findPromise;
                            });
                        });

                        return promise;
                    }).then(function () {
                        var findPromise = new Parse.Promise();

                        team.relation('admins').query().find().then(function (admins) {
                            teamAdmin = admins[0];

                            findPromise.resolve();
                        });

                        return findPromise;
                    }).then(function () {
                        var path = 'https://' + keys.getAppName() + '.parseapp.com/teams/' + teamID + '/offers',
                            image = team.get('profileImageThumb') ? team.get('profileImageThumb') : '';

                        res.render('teams/offer/list', {
                            'team': team,
                            'count': offersCount,
                            'offers': currentOffers,
                            'teamAdmin': teamAdmin,
                            'isLoggedIn': Parse.User.current() ? true : false,
                            'twitterShareButton': require('cloud/commons/twitterShareButton'),
                            'googlePlusShareButton': require('cloud/commons/googlePlusShareButton'),
                            'facebookShareButton': require('cloud/commons/facebookShareButton'),
                            'emailShareButton': require('cloud/commons/emailShareButton'),
                            'meta': {
                                title: 'Offers :: ' + team.get('name'),
                                description: team.get('profile'),
                                image: image,
                                url: path
                            },
                            'returnURL': path
                        });
                    });
                }
            });
        },

        view: function (req, res) {
            var teamID = req.params.teamID,
                offerID = req.params.offerID;

            var Team = Parse.Object.extend("Team"),
                query = new Parse.Query(Team);

            query.get(teamID, {
                success: function(team) {
                    var TeamOffer = Parse.Object.extend('TeamOffer'),
                        offerQuery = new Parse.Query(TeamOffer);

                    offerQuery.get(offerID,{
                        success: function(offer) {
                            var _ = require('underscore');

                            var Donation = Parse.Object.extend('Donation'),
                                query = new Parse.Query(Donation),
                                sponsors = [];

                            query.equalTo('team', team);
                            query.equalTo('offer', offer);

                            query.find().then(function (list) {
                                var promise = Parse.Promise.as();

                                _.each(list, function(donation) {
                                    promise = promise.then(function() {
                                        var findPromise = new Parse.Promise();

                                        var sponsor = donation.get('sponsor');

                                        sponsor.fetch({
                                            success: function (fetchedSponsor) {
                                                sponsors.push(fetchedSponsor);

                                                findPromise.resolve();
                                            }
                                        });

                                        return findPromise;
                                    });
                                });

                                return promise;
                            }).then(function () {
                                // Database end date format is YYYY-MM-DD, user format is DD-MM-YYYY
                                var path = 'https://' + keys.getAppName() + '.parseapp.com/teams/' + teamID + '/offers/' + offerID,
                                    endDate = helpers.revertDate(offer.get('endDate')),
                                    isSoldOut = sponsors.length == offer.get('quantity'),
                                    image = team.get('profileImageThumb') ? team.get('profileImageThumb') : (offer.get('images')[0] ? offer.get('images')[0] : ''),
                                    params = {
                                        'displaySponsors' : require('cloud/commons/displaySponsors'),
                                        'twitterShareButton': require('cloud/commons/twitterShareButton'),
                                        'googlePlusShareButton': require('cloud/commons/googlePlusShareButton'),
                                        'facebookShareButton': require('cloud/commons/facebookShareButton'),
                                        'emailShareButton': require('cloud/commons/emailShareButton'),
                                        'team': team,
                                        'offer': offer,
                                        'isSoldOut': isSoldOut,
                                        'quantity': isSoldOut ? 'Sold out!' : offer.get('quantity') - sponsors.length,
                                        'sponsors': sponsors,
                                        'meta': {
                                            title: offer.get('title') + ' :: ' + team.get('name'),
                                            description: offer.get('details'),
                                            image: image,
                                            url: path
                                        },
                                        'returnURL': path
                                    };

                                offer.set('endDate', endDate);

                                params.isLoggedIn = Parse.User.current() ? true : false;

                                res.render('teams/offer/view', params);
                            });
                        },
                        error: function(object, error) {
                            console.log('Error fetching Offer');
                            console.log(error);
                            res.render('teams/offer/error');
                        }
                    });
                },
                error: function(object, error) {
                    console.log('Error fetching Team');
                    console.log(error);
                    res.render('teams/offer/error');
                }
            });
        }
    };
};