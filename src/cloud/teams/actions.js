module.exports = function (keys) {
    var helpers = require('cloud/teams/helpers')();

    return {
        view: function (req, res) {
            var teamID = req.params.teamID,
                Team = Parse.Object.extend("Team"),
                query = new Parse.Query(Team),
                currentTeam = null;

            query.get(teamID, {
                success: function(team) {
                    var _ = require('underscore');
                    
                    var Donation = Parse.Object.extend('Donation'),
                        query = new Parse.Query(Donation),
                        sponsors = [],
                        currentTeam = team;

                    query.equalTo('team', team);

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
                    }).then(function() {
                    	var playersPromise = new Parse.Promise(),
                    		Player = Parse.Object.extend('Player'),
                    		playersQuery = new Parse.Query(Player),
                    		coachesPromise = new Parse.Promise(),
                    		Coach = Parse.Object.extend('Coach'),
                    		coachesQuery = new Parse.Query(Coach);
                    	
                    	playersQuery.equalTo('team', currentTeam.get('name'));
                    	playersPromise = playersQuery.find();
                    	
                    	coachesQuery.equalTo('team', currentTeam.get('name'));
                    	coachesPromise = coachesQuery.find();
                    	
                    	
                    	Parse.Promise.when([playersPromise, coachesPromise]).then(function(players, coaches) {
                            var path = 'https://' + keys.getAppName() + '.parseapp.com/teams/' + teamID;

                            res.render('teams/view', {
                                'displaySponsors' : require('cloud/commons/displaySponsors'),
                                'team': currentTeam,
                                'twitterShareButton': require('cloud/commons/twitterShareButton'),
                                'googlePlusShareButton': require('cloud/commons/googlePlusShareButton'),
                                'facebookShareButton': require('cloud/commons/facebookShareButton'),
                                'emailShareButton': require('cloud/commons/emailShareButton'),
                                'sponsors': sponsors,
                                'meta': {
                                    title: currentTeam.get('name'),
                                    description: currentTeam.get('profile'),
                                    image: currentTeam.get('profileImageThumb') ? currentTeam.get('profileImageThumb') : '',
                                    url: path
                                },
                                'returnURL': path,
                                'players' : players,
                                'coaches' : coaches
                        	});
                    	});
                    	
                    	
                    });
                },
                error: function(object, error) {
                    res.render('teams/view');
                }
            });
        },

        offer: function (req, res) {
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
                                    }, currentUser = Parse.User.current();

                                offer.set('endDate', endDate);

                                if (!currentUser) {
                                    params.isLoggedIn = false;

                                    res.render('teams/offer/offer', params);
                                } else {
                                    Parse.User.current().fetch().then(function (user) {
                                        params.isLoggedIn = true;

                                        res.render('teams/offer/offer', params);
                                    });
                                }
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