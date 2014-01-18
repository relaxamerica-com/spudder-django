module.exports = function (keys) {
	var krowdio = require('cloud/krowdio'),
		pluralizer = require('cloud/pluralize'),
		utilities = require('cloud/utilities')(),
		_ = require('underscore'),
		entityUtilities = require('cloud/entity/utilities')();
	
	var createTeam = function(name, admin, entity) {
		var TeamClass = Parse.Object.extend('Team'),
			query = new Parse.Query(TeamClass),
			promise = new Parse.Promise();
			
		query.equalTo('nameSearch', name.toLowerCase());
		query.equalTo('location', entity.get('location'));
		
		query.first().then(function(_team) {
			if (_team) {
				var admins = _team.relation('admins');
		        admins.add(admin);
		        entity.set('team', _team);
		        Parse.Promise.when([_team.save(), entity.save()]).then(function() {
		        	promise.resolve(_team);
		        });
			} else {
		        var team = new TeamClass();
		        team.set('name', name);
		        team.set('location', entity.get('location'));
		        team.set('nameSearch', name.toLowerCase());
		        var admins = team.relation('admins');
		        admins.add(admin);
		        entity.set('team', team);
		        Parse.Promise.when([team.save(), entity.save()]).then(function() {
		        	promise.resolve(team);
		        });
			}
		}, function(error) {
			console.log(error);
		});
        
        return promise;
	};
	
	return {
		createEntity: {
        	get: function(req, res) {
        		var entityType = req.params.entityType,
        			teamId = 'teamId' in req.params ? req.params.teamId : null,
        			breadcrumbs = [
        				{ 'title' : pluralizer.pluralize(entityType, 2), 'href' : '/dashboard/listEntities/' + entityType }, 
        				{ 'title' : 'Create a ' + entityType.toLowerCase(), 'href' : '/dashboard/createEntity/' + entityType }
        			],
                    parseKeys = { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() };
                
                if (teamId) {
                	var Team = Parse.Object.extend('Team'),
                		query = new Parse.Query(Team);
                	
                	query.get(teamId).then(function(team) {
                		res.render('dashboard/' + entityType.toLowerCase() + '/create', { 'breadcrumbs' : breadcrumbs, 'keys' : parseKeys, 'errors' : [], 'team' : team });
                	}, function(err) {
                		console.log(err);
                	});
                	
                } else {
	        		res.render('dashboard/' + entityType.toLowerCase() + '/create', { 'breadcrumbs' : breadcrumbs, 'keys' : parseKeys, 'errors' : [], 'team' : null });
                } 
        	},
        	
        	post: function(req, res) {
		        var entityType = req.params.entityType,
		        	user = Parse.User.current(),
		        	sport = req.body.sport,
		        	name = req.body.name,
		        	location = req.body.location,
		        	contact = req.body.contact,
		        	profile = req.body.profile,
		        	team = req.body.team,
		        	adminsList = req.body.admins.map(function(el) { 
                    				if (el.length != 0) {
				                		return utilities.removeSpaces(el);
                    				}
			                	});
		        	isDisplayPublicly = !('hide-publicly' in req.body),
		        	profileImageThumb = req.body.profileImageThumb,
        			breadcrumbs = [entityType, 'Create a ' + entityType.toLowerCase()],
                    keys = { 'jsKey' : req.body.jsKey, 'appId' : req.body.appId };
	
		        var relationName,
			        relationType,
			        relationId,
			        relation;
	
				var context = { 'breadcrumbs' : breadcrumbs, 'keys' : keys },
					promise = new Parse.Promise();
				
		        new Parse.Query(entityType).equalTo('nameSearch', name.toLowerCase()).find()
		            .then(function(entities) {
		                if (entities.length > 0) {
		                	var error = 'A ' + entityType + ' with the name ' + name +
		                        ' already exists, please choose another name';
		                    return Parse.Promise.error(error);
		                }
		                var EntityClass = Parse.Object.extend(entityType);
		                var entity = new EntityClass();
		                entity.set('name', name);
		                entity.set('nameSearch', name.toLowerCase());
		                entity.set('location', location);
		                entity.set('contact', contact);
		                entity.set('profile', profile);
		                entity.set('sport', sport);
		                entity.set('profileImageThumb', profileImageThumb);
		                entity.set('isDisplayPublicly', isDisplayPublicly);
		                entity.set('publicName', req.body.publicName);
		                
		                if (entityType == 'Player') {
							entity.set('position', req.body.position);
							entity.set('number', req.body.number);
						}
		                
		                return entity.save(null);
		            })
		            .then(function(entity){
		                krowdio.krowdioRegisterEntityAndSave(entity);
		                
		                promise.resolve(entity);
		            },
		            function(error){
		            	context['errors'] = [error];
		                res.render('dashboard/' + entityType.toLowerCase() + '/create', context);
		            });
		            
		            var notFoundEmails = [],
		            	addAdminsPromise = new Parse.Promise();
		            	
		            promise.then(function(entity) {
		            	var teamPromise = new Parse.Promise();
		            	if (team.length > 0) {
			            	teamPromise = createTeam(team, user, entity);
		            	} else {
		            		teamPromise.resolve();
		            	}
		            	
		            	if (adminsList.length > 0) {
		            		console.log('adding addmins');
			            	addAdminsPromise = entityUtilities.addAdmins(entity, adminsList, notFoundEmails);
		            	} else {
		            		addAdminsPromise.resolve();
		            	}
		            	
		            	Parse.Promise.when([addAdminsPromise, teamPromise]).then(function() {
		            		if (notFoundEmails.length > 0) {
		            			res.redirect('/dashboard/listEntities/' + entityType + '?error=Team with given name already exists.');
		            		}
		            		res.redirect('/dashboard/listEntities/' + entityType);
		            	}, function(error) {
		            		console.log(error[1].message);
		            		res.redirect('/dashboard/listEntities/' + entityType + '?error=' + error[1].message);
		            	});
		            	
		            });
		        }
        },
        
        listEntities: function(req, res) {
        	var	entityType = req.params.entityType,
        		pluralized = pluralizer.pluralize(entityType, 2);

            Parse.User.current().fetch().then(function (user) {
                var EntityClass = Parse.Object.extend(entityType),
                    query = new Parse.Query(EntityClass),
                    entities = [];

                query.equalTo('admins', user);

                query.find().then(function (list) {
                	var promise = Parse.Promise.as();

                    _.each(list, function(entity) {
                    	
                        promise = promise.then(function() {
                            var findPromise = new Parse.Promise();

                            entity.relation('admins').query().find().then(function (admins) {
                                entity['otherAdmins'] = admins;
                                entities.push(entity);
                                findPromise.resolve();
                            });

                            return findPromise;
                        });
                    });

                    return promise;
                 }).then(function() {
                	var breadcrumbs = [
                		{ 'title' : pluralized, 'href' : '/dashboard/listEntities/' + entityType }, 
        				{ 'title' : 'My ' + pluralized, 'href' : '/dashboard/listEntities/' + entityType }
        			];
                    res.render('dashboard/' + entityType.toLowerCase() + '/list', {
                        'breadcrumbs' : breadcrumbs,
                        'list': entities
                    });
                });
            });
        },
        
        editEntity: {
        	get: function(req, res) {
        		var entityType = req.params.entityType,
        			EntityClass = Parse.Object.extend(entityType),
                    query = new Parse.Query(EntityClass),
                    id = req.params.id,
            		entityName = entityType.toLowerCase(),
            		breadcrumbs = [
	            		{ 'title' : pluralizer.pluralize(entityType, 2), 'href' : '/dashboard/listEntities/' + entityType }, 
						{ 'title' : 'Edit this ' + entityType.toLowerCase(), 'href' : '/dashboard/editEntity/' + entityType + '/' + id }
    				];

                query.get(id, {
                    success: function(entity) {
                    	var _entity = entity,
                    		_team = entity.get('team'),
	                    	context = {
	                            'breadcrumbs' : breadcrumbs,
	                            'found'  : true,
	                            'entity' : _entity,
	                            'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
	                       	};
	                       	
                    	if (_team !== undefined) {
                    		_entity.team = _team.get('name');
	                    	_team.fetch().then(function(team) {
		                        res.render('dashboard/' + entityName + '/edit', context);
	                    	});
                    	} else {
                    		res.render('dashboard/' + entityName + '/edit', context);
                    	}
                    },
                    error: function(object, error) {
                        console.log(error);
                        res.render('dashboard/' + entityName + '/edit', {
                            'breadcrumbs' : breadcrumbs,
                            'found': false
                        });
                    }
                });
        	},
        	
        	post: function(req, res) {
        		var name = req.body.name,
                    location = req.body.location,
                    details = req.body['contact-details'],
                    profile = req.body.profile,
                    id = req.params.id,
                    entityType = req.params.entityType,
		        	isDisplayPublicly = !('hide-publicly' in req.body);

                var EntityClass = Parse.Object.extend(entityType),
                    query = new Parse.Query(EntityClass),
                    promise = new Parse.Promise(),
                    adminsList = req.body.admins.map(function(el) { 
                    				if (el.length != 0) {
				                		return utilities.removeSpaces(el);
                    				}
			                	});

                query.get(id, {
                    success: function(entity) {
                        entity.set('name', name);
                        entity.set('nameSearch', name.toLowerCase());
                        entity.set('location', req.body.location);
                        entity.set('contact', req.body.contact);
                        entity.set('profile', req.body.profile);
                        entity.set('sport', req.body.sport);
                        entity.set('profileImageThumb', req.body.profileImageThumb);
                        entity.set('website', req.body.website);
                        entity.set('email', req.body.email);
                        entity.set('facebook', req.body.facebook);
                        entity.set('twitter', req.body.twitter);
                        entity.set('googlePlus', req.body.googlePlus);
                        entity.set('isDisplayPublicly', isDisplayPublicly);
                        entity.set('publicName', req.body.publicName);
                        
                        if (entityType == 'Player') {
							entity.set('position', req.body.position);
							entity.set('number', req.body.number);
						}

                        entity.save(null).then(function() {
	                        promise.resolve(entity);
                        });
                    },
                    error: function(object, error) {
                        console.log(error);
                        res.redirect('/dashboard/editEntity/' + entityType + '/' + id);
                    }
                });
                
	            var addAdminsPromise = new Parse.Promise(),
	            	notFoundEmails = [];
		            	
	            promise.then(function(entity) {
	            	if (adminsList.length > 0) {
		            	addAdminsPromise = entityUtilities.addAdmins(entity, adminsList, notFoundEmails);
	            	} else {
	            		res.redirect('/dashboard/listEntities/' + entityType);
	            	}
	            	addAdminsPromise.then(function() {
	            		if (notFoundEmails.length > 0) {
	            			res.redirect('/dashboard/listEntities/' + entityType + '?error');
	            		} else {
			            	res.redirect('/dashboard/listEntities/' + entityType);
	            		}
	            	});
	            });
        	}
        },
        
        removeEntity: function(req, res) {
        	var id = req.params.id,
        		entityType = req.params.entityType,
        		EntityClass = Parse.Object.extend(entityType),
                query = new Parse.Query(EntityClass);

            query.get(id).then(function (entity) {
        		entity.destroy().then(function () {
                    res.redirect('/dashboard/listEntities/' + entityType);
				});
            });
        },
        
        removeAdmin: function(req, res) {
        	var adminEmail = req.body.adminEmail,
        		userId = req.params.id,
        		entityType = req.params.entityType,
        		EntityClass = Parse.Object.extend(entityType),
        		query = new Parse.Query(EntityClass),
        		promise = new Parse.Promise();

        	query.get(userId).then(function(entity) {
        		new Parse.Query(Parse.User).equalTo('email', adminEmail).first().then(function(user) {
        			if (user == undefined || user == null) {
        				promise.resolve();
        			}
	            	entity.relation('admins').remove(user);
	            	entity.remove('adminsEmails', adminEmail);
	            	return entity.save(null);
        		}).then(function() {
        			promise.resolve();
        		});
           	});
           	
           	promise.then(function(){
           		res.send('OK');
           	});
        	
        },
        
        acceptEntityInvitation: function(req, res) {
        	var Invitation = Parse.Object.extend('EntityInvitation'),
        		invQuery = new Parse.Query(Invitation);
        	
        	invQuery.get(req.params.entityInvitationId).then(function(invitation) {
        		var inv = invitation,
        			EntityClass = Parse.Object.extend(inv.get('entityType')),
        			query = new Parse.Query(EntityClass);
        			
        		query.get(invitation.get('entityId')).then(function(entity) {
        			var invited = inv.get('invited'),
        				_entity = entity;
        				
        			invited.fetch().then(function(_invited) {
	        			_entity.relation('admins').add(_invited);
	        			_entity.add('adminsEmails', _invited.getEmail());
	        			_entity.save().then(function() {
	        				inv.destroy().then(function() {
		        				res.redirect('/invitationsList#accepted');
	        				});
	        			});
        			});
        		});
        	});
        },
        
        rejectEntityInvitation: function(req, res) {
        	var Invitation = Parse.Object.extend('EntityInvitation'),
        		invQuery = new Parse.Query(Invitation);
        		
        	invQuery.get(req.params.entityInvitationId).then(function(invitation) {
        		invitation.destroy().then(function() {
        			res.redirect('/invitationsList#rejected');
        		});
        	});
        },
        
        invitationsList: function(req, res) {
        	var Invitation = Parse.Object.extend('EntityInvitation'),
        		invQuery = new Parse.Query(Invitation),
        		list = [];
        	
        	invQuery.equalTo('invited', Parse.User.current());
        	
        	invQuery.find().then(function(_list) {
        		var promise = Parse.Promise.as();
        			
        		_.each(_list, function(_inv) {
    				var inv = _inv;
    			
    				promise = promise.then(function() {
	    				var fetchPromise = new Parse.Promise();
	    				
	        			inv.get('inviting').fetch().then(function(_entity) {
	        				inv.invitingName = _entity.get('name');
	        				inv.invitingEmail = _entity.getEmail();
	        				list.push(inv);
	        				fetchPromise.resolve();
	        			});
	        			
	        			return fetchPromise;
    				});
        		});
        		
        		return promise;
        	}).then(function() {
        		res.render('dashboard/entity/invitationsList', { 
        			'list' : list, 
        			'breadcrumbs' : [{ 'title' : 'Invitations', 'href' : '/invitationsList' }], 
        			'convertDate' : utilities.convertDate });
        	});
        }
	};
};