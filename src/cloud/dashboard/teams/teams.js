module.exports = function (keys) {
    return {
        create: {
            get: function (req, res) {
                res.render('dashboard/teams/create', {
                    'breadcrumbs' : ['Teams', 'Create a team']
                });
            },

            post: function (req, res) {
                var name = req.body.name,
                    location = req.body.location,
                    details = req.body['contact-details'],
                    profile =  req.body.profile;

                var Team = Parse.Object.extend('Team'),
                    team = new Team();

                team.set('name', name);
                team.set('nameSearch', name.toLowerCase());
                team.set('location', location);
                team.set('profile', profile);
                team.set('contact', details);
                team.set('profileImageThumb', 'http://static2.krowd.io/media/52769e9ff1f70e0552df58a4/0/52979ffce9b6cc55d0cd073d/d22078392a_t.png');

                team.save(null, {
                    success: function (team) {
                        Parse.User.current().fetch().then(function (user) {
                            var admins = team.relation('admins');

                            admins.add(user);
                            team.save();

                            var roleACL = new Parse.ACL();
                            roleACL.setPublicReadAccess(true);
                            var teamAdminRole = new Parse.Role("TeamAdmin", roleACL);
                            teamAdminRole.getUsers().add(user);
                            teamAdminRole.save();

                            res.redirect('/dashboard/teams/view/' + team.id);
                        });
                    },

                    error: function (team, error) {
                        console.log(error);
                        res.redirect('/dashboard/teams/create?error' + encodeURIComponent(error));
                    }
                });
            }
        },

        view: {
            get: function (req, res) {
                var Team = Parse.Object.extend("Team"),
                    query = new Parse.Query(Team),
                    teamID = req.params.id;

                query.get(teamID, {
                    success: function(team) {
                        res.render('dashboard/teams/view', {
                            'breadcrumbs' : ['Teams', 'Update this team'],
                            'found': true,
                            'team': {
                                name: team.get('name'),
                                location: team.get('location'),
                                details: team.get('contact'),
                                profile: team.get('profile'),
                                id: team.id
                            }
                        });
                    },
                    error: function(object, error) {
                        console.log(error);
                        res.render('dashboard/teams/view', {
                            'breadcrumbs' : ['Teams', 'Update this team'],
                            'found': false
                        });
                    }
                });
            }
        },

        update: {
            post: function (req, res) {
                var name = req.body.name,
                    location = req.body.location,
                    details = req.body['contact-details'],
                    profile =  req.body.profile,
                    teamID = req.body.teamID;

                var Team = Parse.Object.extend('Team'),
                    query = new Parse.Query(Team);

                query.get(teamID, {
                    success: function(team) {
                        team.set('name', name);
                        team.set('nameSearch', name.toLowerCase());
                        team.set('location', location);
                        team.set('profile', profile);
                        team.set('contact', details);

                        team.save();

                        res.redirect('/dashboard/teams/view/' + teamID);
                    },
                    error: function(object, error) {
                        console.log(error);
                        res.redirect('/dashboard/teams/view/' + teamID);
                    }
                });
            }
        },

        list: {
            get: function (req, res) {
                var _ = require('underscore');

                Parse.User.current().fetch().then(function (user) {
                    var Team = Parse.Object.extend('Team'),
                        query = new Parse.Query(Team),
                        teamsList = [];

                    query.equalTo('admins', user);

                    query.find().then(function (list) {
                        var promise = Parse.Promise.as();

                        _.each(list, function(team) {
                            var Recipient = Parse.Object.extend('Recipient'),
                                recipientQuery = new Parse.Query(Recipient);

                            recipientQuery.equalTo('team', team);

                            promise = promise.then(function() {
                                var findPromise = new Parse.Promise();

                                recipientQuery.find().then(function (results) {
                                    team.set('isRegisteredRecipient', results.length > 0);
                                    teamsList.push(team);
                                    findPromise.resolve();
                                });

                                return findPromise;
                            });
                        });

                        return promise;
                    }).then(function () {
                        res.render('dashboard/teams/list', {
                            'breadcrumbs' : ['Teams', 'My teams'],
                            'list': teamsList
                        });
                    });
                });
            }
        },

        remove: {
            get: function (req, res) {
                var Team = Parse.Object.extend("Team"),
                    query = new Parse.Query(Team),
                    teamID = req.params.id;

                query.get(teamID).then(function (team) {
                    team.destroy().then(function () {
                        res.redirect('/dashboard/teams');
                    },
                    function (error) {
                        console.log(error);
                    });
                });
            }
        }
    };
};