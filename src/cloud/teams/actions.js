module.exports = function (keys) {
    var helpers = require('cloud/teams/helpers')();

    return {
        view: function (req, res) {
            var teamID = req.params.teamID,
                Team = Parse.Object.extend("Team"),
                query = new Parse.Query(Team);

            query.get(teamID, {
                success: function(team) {
                    res.render('teams/view', {
                        'displayItems' : require('cloud/commons/displayItems.js'),
                        'team': team
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
                            // Database end date format is YYYY-MM-DD, user format is DD-MM-YYYY
                            var endDate = helpers.revertDate(offer.get('endDate'));
                            offer.set('endDate', endDate);

                            var url = 'https://' + keys.getAppName() + 'parseapp.com/teams/' + teamID + '/offers/' + offerID;
                            res.render('teams/offer/offer', {
                                'displayItems' : require('cloud/commons/displayItems.js'),
                                'twitterShareButton': require('cloud/commons/twitterShareButton'),
                                'googlePlusShareButton': require('cloud/commons/googlePlusShareButton'),
                                'facebookShareButton': require('cloud/commons/facebookShareButton'),
                                'team': team,
                                'offer': offer,
                                'meta': {
                                    title: offer.get('title') + ' :: ' + team.get('name'),
                                    description: offer.get('details'),
                                    image: offer.get('images')[0] ? offer.get('images')[0] : '',
                                    url: url
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