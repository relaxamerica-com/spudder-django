module.exports = function (keys) {
	var entityUtilities = require('cloud/entity/utilities')(),
		utilities = require('cloud/utilities')(),
		krowdio = require('cloud/krowdio');
	
    return {
        create: {
            get: function (req, res) {
                res.render('dashboard/teams/create', {
                    'breadcrumbs' : [{ 'title' : 'Teams', 'href' : '/dashboard/teams' }, { 'title' : 'Create a team', 'href' : 'javascript:void(0);' }],
                    'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
                });
            },

            post: function (req, res) {
                var name = req.body.name,
                    profileImageThumb = req.body.profileImageThumb,
                    Team = Parse.Object.extend('Team'),
                    team = new Team();
                	adminsList = [];
                	
   				for(var i = 0; i < req.body.admins.length; i++) {
   					var el = req.body.admins[i];
					if (el.length != 0 && el !== null && el !== undefined) {
						adminsList.push(utilities.removeSpaces(el));
					}
				}
                team.set('name', name);
                team.set('nameSearch', name.toLowerCase());
                team.set('location', req.body.location);
                team.set('contact', req.body['contact-details']);
                team.set('profile', req.body.profile);
                team.set('sport', req.body.sport);
                team.set('profileImageThumb', profileImageThumb);

                team.save(null, {
                    success: function (team) {
                    	
                        Parse.Promise.when([Parse.User.current().fetch(), krowdio.krowdioRegisterEntityAndSave(team)]).then(function (user) {
                            var admins = team.relation('admins');

                            admins.add(user);
                            team.save().then(function(team) {
	                            var roleACL = new Parse.ACL();
	                            roleACL.setPublicReadAccess(true);
	                            var teamAdminRole = new Parse.Role("TeamAdmin", roleACL);
	                            teamAdminRole.getUsers().add(user);
                            	if (adminsList.length > 0) {
                            		var notFoundEmails = [];
                            		entityUtilities.addAdmins(team, adminsList, notFoundEmails).then(function() {
	                            		res.redirect('/dashboard/teams/edit/' + team.id);
                            		});
                            	} else {
		                            res.redirect('/dashboard/teams/edit/' + team.id);
                            	}
                            });

                        });
                    },

                    error: function (team, error) {
                        console.log(error);
                        res.redirect('/dashboard/teams/create?error' + encodeURIComponent(error));
                    }
                });
            }
        },

        edit: {
            get: function (req, res) {
                var Team = Parse.Object.extend("Team"),
                    query = new Parse.Query(Team),
                    teamID = req.params.id;

                query.get(teamID, {
                    success: function(team) {
                        res.render('dashboard/teams/edit', {
                            'breadcrumbs' : [{ 'title' : 'Teams', 'href' : '/dashboard/teams' }, { 'title' : 'Edit this team', 'href' : 'javascript:void(0);' }],
                            'found': true,
                            'team': team,
                            'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
                        });
                    },
                    error: function(object, error) {
                        console.log(error);
                        res.render('dashboard/teams/edit', {
                            'breadcrumbs' : [{ 'title' : 'Teams', 'href' : '/dashboard/teams' }, { 'title' : 'Edit this team', 'href' : 'javascript:void(0);' }],
                            'found': false
                        });
                    }
                });
            },

            post: function (req, res) {
                var name = req.body.name,
                    location = req.body.location,
                    details = req.body['contact-details'],
                    profile =  req.body.profile,
                    teamID = req.body.teamID,
                    adminsList = [];
                
                for(var i = 0; i < req.body.admins.length; i++) {
                    var el = req.body.admins[i];
                    if (el.length != 0 && el !== null && el !== undefined) {
                        adminsList.push(utilities.removeSpaces(el));
                    }
                }

                var Team = Parse.Object.extend('Team'),
                    query = new Parse.Query(Team);

                query.get(teamID, {
                    success: function(team) {
                        team.set('name', name);
                        team.set('nameSearch', name.toLowerCase());
                        team.set('location', req.body.location);
                        team.set('contact', req.body.contact);
                        team.set('profile', req.body.profile);
                        team.set('sport', req.body.sport);
                        team.set('profileImageThumb', req.body.profileImageThumb);
                        team.set('website', req.body.website);
                        team.set('email', req.body.email);
                        team.set('homeVenue', req.body.homeVenue);
                        team.set('facebook', req.body.facebook);
                        team.set('twitter', req.body.twitter);
                        team.set('googlePlus', req.body.googlePlus);

                        team.save();

                        if (adminsList.length > 0) {
                            var notFoundEmails = [];
                            entityUtilities.addAdmins(team, adminsList, notFoundEmails).then(function() {
                                res.redirect('/dashboard/teams');
                            });
                        } else {
                            res.redirect('/dashboard/teams');
                        }
                    },
                    error: function(object, error) {
                        console.log(error);
                        res.redirect('/dashboard/teams/edit/' + teamID);
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
                        return res.render('dashboard/teams/list', {
                            'breadcrumbs' : [{ 'title' : 'Teams', 'href' : '/dashboard/teams' }, { 'title' : 'My teams', 'href' : 'javascript:void(0);' }],
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
                    var Recipient = Parse.Object.extend('Recipient'),
                        recipientQuery = new Parse.Query(Recipient);

                    recipientQuery.equalTo('team', team);

                    recipientQuery.find().then(function (results) {
                        var promise = new Parse.Promise();

                        if (results.length > 0) {
                            results[0].destroy().then(function() {
                                promise.resolve();
                            });
                        } else {
                            promise.resolve();
                        }

                        return promise;
                    }).then(function () {
                        team.destroy().then(function () {
                            res.redirect('/dashboard/teams');
                        });
                    },
                    function (error) {
                        console.log(error);
                    });
                });
            }
        },
        
        teamEntities: {
        	get: function(req, res) {
        		 var Team = Parse.Object.extend("Team"),
                    query = new Parse.Query(Team),
                    teamID = req.params.id,
                    entityType = req.params.entityType,
                    pluralizer = require('cloud/pluralize'),
                    pluralized = pluralizer.pluralize(entityType);
                    
                 query.get(teamID).then(function (team) {
                 	var EntityClass = Parse.Object.extend(entityType),
                 		entityQuery = new Parse.Query(EntityClass);
                 		
                 	entityQuery.equalTo('team', team);
                 	
                 	entityQuery.find().then(function(list) {
                 		res.render('dashboard/teams/list' + pluralized, {
                 			'list' : list,
                 			'breadcrumbs' : [
                 				{'title' : 'Teams', 'href' : '/dashboard/teams'},
                 				{'title' : 'My Teams', 'href' : '/dashboard/teams'},
                 				{'title' : 'My Team ' + pluralized, 'href' : '/dashboard/teams/' + teamID + '/list/' + entityType }
                 			],
                 			'teamId' : team.id
                 		});
                 	}, function(err) {
                 		console.log(err);
                 	});
                 });
        	}
        }
    };
};