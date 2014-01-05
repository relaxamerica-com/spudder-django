module.exports = function (keys) {
    var helpers = require('cloud/teams/helpers')();

    return {
        view: function (req, res) {
            var teamID = req.params.teamID,
                Team = Parse.Object.extend("Team"),
                query = new Parse.Query(Team);
                
            query.get(teamID, {
                success: function(team) {
                    var _ = require('underscore'),
                        currentTeam = team;

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
                            'returnURL': path
                        });
                    });
                },
                error: function(object, error) {
                    console.log(error);
                }
            });
        }
    };
};