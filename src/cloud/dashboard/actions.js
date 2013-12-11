module.exports = function (keys) {
	var krowdio = require('cloud/krowdio'),
		pluralizer = require('cloud/pluralize');
	
    return {
        spuds: function (req, res) {
            var breadcrumbs = ['SPUDS'];
            res.render('dashboard/spuds', {
                'breadcrumbs' : breadcrumbs
            });
        },

        general: function (req, res) {
            var breadcrumbs = ['Fans', 'General'];
            res.render('dashboard/fan/general', {
                'breadcrumbs' : breadcrumbs,
                'displayUsers' : require('cloud/commons/displayUsers'),
                'modalTop' : require('cloud/dashboard/fan/modalTop'),
                'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
            });
        },
        
        mySpuds: function(req, res) {
        	var breadcrumbs = ['Fans', 'My Spuds'];
        	res.render('dashboard/fan/mySpuds', {
                'breadcrumbs' : breadcrumbs,
                'modalTop' : require('cloud/dashboard/fan/modalTop'),
            });
        },
        
        myFavorites: function(req, res) {
        	var breadcrumbs = ['Fans', 'My Favorites'];
        	res.render('dashboard/fan/myFavorites', {
                'breadcrumbs' : breadcrumbs,
                'displayUsers' : require('cloud/commons/displayUsers'),
            });
        },
        
        basicInfo: function(req, res) {
        	var breadcrumbs = ['Fans', 'Basic Info'];
        	res.render('dashboard/fan/basicInfo', {
                'breadcrumbs' : breadcrumbs,
                'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
            });
        },
        
        settings: function(req, res) {
        	var breadcrumbs = ['Fans', 'Settings'];
        	res.render('dashboard/fan/settings', {
                'breadcrumbs' : breadcrumbs,
            });
        },
        
        createEntity: {
        	get: function(req, res) {
        		var entityType = req.params.entityType;
        			breadcrumbs = [entityType, 'Create a ' + entityType.toLowerCase()],
                    keys = { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() };
        		return res.render('dashboard/' + entityType.toLowerCase() + '/create', { 'breadcrumbs' : breadcrumbs, 'keys' : keys, 'errors' : [] });
        	},
        	
        	post: function(req, res) {
		        var entityType = req.params.entityType,
		        	user = Parse.User.current(),
		        	sport = req.body.sport,
		        	name = req.body.name,
		        	location = req.body.location,
		        	contact = req.body.contact,
		        	profile = req.body.profile,
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
		                entity.relation('admins').add(Parse.User.current());
		                // if (currentEntityCreateKey != null) {
		                    // relationName = currentEntityCreateKey.split('-')[0];
		                    // relationType = currentEntityCreateKey.split('-')[1];
		                    // relationId = currentEntityCreateKey.split('-')[2];
		                    // relation = adminCache[relationType][relationId];
		                    // if (!currentEntityCreateReverse)
		                        // entity.relation(relationName).add(relation);
		                    // currentEntityCreateKey = null;
		                // }
		                return entity.save(null);
		            })
		            .then(function(entity){
		                // if (currentEntityCreateReverse) {
		                    // relation.relation(relationName).add(entity);
		                    // relation.save(null);
		                    // currentEntityCreateReverse = false;
		                // }
		                krowdio.krowdioRegisterEntityAndSave(entity);
		                return res.redirect('/dashboard/listEntities/' + entityType);
		            },
		            function(error){
		            	context['errors'] = [error];
		            	console.log(context);
		                return res.render('dashboard/' + entityType.toLowerCase() + '/create', context);
		            });
		        }
        },
        
        listEntities: function(req, res) {
        	var	entityType = req.params.entityType,
        		pluralized = pluralizer.pluralize(entityType, 2);

            Parse.User.current().fetch().then(function (user) {
                var EntityClass = Parse.Object.extend(entityType),
                    query = new Parse.Query(EntityClass);

                query.equalTo('admins', user);

                query.find().then(function (list) {
                    return res.render('dashboard/' + entityType.toLowerCase() + '/list', {
                        'breadcrumbs' : [entityType, 'My ' + pluralized],
                        'list': list
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
            		entityName = entityType.toLowerCase();

                query.get(id, {
                    success: function(entity) {
                    	var context = {
                            'breadcrumbs' : [entityType, 'Edit this ' + entityName],
                            'found': true,
                            'entity' : entity,
                            'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
                       	};
                        return res.render('dashboard/' + entityName + '/edit', context);
                    },
                    error: function(object, error) {
                        console.log(error);
                        return res.render('dashboard/' + entityName + '/edit', {
                            'breadcrumbs' : [entityType, 'Edit this ' + entityName],
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
                    entityType = req.params.entityType;

                var EntityClass = Parse.Object.extend(entityType),
                    query = new Parse.Query(EntityClass);

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

                        entity.save(null).then(function() {
	                        return res.redirect('/dashboard/editEntity/' + entityType + '/' + id);
                        });
                    },
                    error: function(object, error) {
                        console.log(error);
                        return res.redirect('/dashboard/editEntity/' + entityType + '/' + id);
                    }
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
                    return res.redirect('/dashboard/listEntities/' + entityType);
				});
            });
        }
    };
};