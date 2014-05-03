module.exports = function (keys) {
    var helpers = require('cloud/teams/helpers')(),
        krowdio = require('cloud/krowdio'),
        _ = require('underscore');

    return {
        view: function (req, res) {
            var teamID = req.params.teamID,
                Team = Parse.Object.extend("Team"),
                query = new Parse.Query(Team),
                userAgent = req.headers['user-agent'];
                
            query.get(teamID, {
                success: function(team) {
                    var currentTeam = team,
                        TeamSponsors = Parse.Object.extend('TeamSponsors'),
                        query = new Parse.Query(TeamSponsors),
                        sponsors = [];

                    query.equalTo('team', team);

                    query.find().then(function (team_sponsors) {
                        var promise = Parse.Promise.as();

                        if (team_sponsors.length) {
                            return team_sponsors[0].relation('sponsors').query().find();
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
                        var Player = Parse.Object.extend("Player"),
                            playerQuery = new Parse.Query(Player),
                            Coach = Parse.Object.extend("Coach"),
                            coachQuery = new Parse.Query(Coach);

                        playerQuery.equalTo('team', team);
                        playerQuery.ascending("number");
                        coachQuery.equalTo('team', team);

                        return Parse.Promise.when([
                            playerQuery.find().then(function(players){
                                return players;
                            }),
                            coachQuery.find().then(function(coaches){
                                return coaches;
                            })
                        ]);
                    }).then(function (players, coaches) {// arguments passed to this callback are: players, coaches
                        var path = 'https://' + keys.getAppName() + '.parseapp.com/teams/' + teamID;

						krowdio.krowdioGetUserMentionActivity(userAgent, currentTeam).then(function(spuds) {
	                        res.render('teams/view', {
	                            'displaySponsors' : require('cloud/commons/displaySponsors'),
	                            'team': currentTeam,
	                            'twitterShareButton': require('cloud/commons/twitterShareButton'),
	                            'googlePlusShareButton': require('cloud/commons/googlePlusShareButton'),
	                            'facebookShareButton': require('cloud/commons/facebookShareButton'),
	                            'emailShareButton': require('cloud/commons/emailShareButton'),
	                            'sponsors': sponsors,
	                            'players': players,
	                            'coaches': coaches,
	                            'meta': {
	                                title: currentTeam.get('name'),
	                                description: currentTeam.get('profile'),
	                                image: currentTeam.get('profileImageThumb') ? currentTeam.get('profileImageThumb') : '',
	                                url: path
	                            },
	                            'returnURL': path,
	                            'spuds' : JSON.parse(spuds),
	                            'spudContainer' : require('cloud/commons/spudContainer')
	                        });
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