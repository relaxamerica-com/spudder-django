module.exports = function (keys) {
    var helpers = require('cloud/teams/helpers')(),
        _ = require('underscore');

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
                                    offer.set('isSoldOut', (offer.get('quantity') - donations.length) == 0);

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
                            'donateButton': require('cloud/teams/commons/donateButton'),
                            'spudmartBaseURL': keys.getSpudmartURL(),
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
                            var TeamOfferSponsors = Parse.Object.extend('TeamOfferSponsors'),
                                query = new Parse.Query(TeamOfferSponsors),
                                sponsors = [];

                            query.equalTo('team', team);
                            query.equalTo('teamOffer', offer);

                            query.find().then(function (team_offer_sponsors) {
                                var promise = Parse.Promise.as();

                                if (team_offer_sponsors.length) {
                                    return team_offer_sponsors[0].relation('sponsors').query().find();
                                }

                                return promise;
                            }).then(function (sponsors_list) {
                                var promise = Parse.Promise.as();

                                _.each(sponsors_list, function(team_sponsor) {
                                    promise = promise.then(function() {
                                        var findPromise = new Parse.Promise();

                                        var SponsorPage = Parse.Object.extend('SponsorPage'),
                                            sponsorPageQuery = new Parse.Query(SponsorPage);

                                        sponsorPageQuery.equalTo('sponsor', team_sponsor);

                                        sponsorPageQuery.find({
                                            success: function (results) {
                                                team_sponsor.page = results.length ? results[0] : undefined;
                                                sponsors.push(team_sponsor);

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
                                        'donateButton': require('cloud/teams/commons/donateButton'),
                                        'team': team,
                                        'offer': offer,
                                        'spudmartBaseURL': keys.getSpudmartURL(),
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