var krowdio = require('cloud/krowdio'),
	_ = require('underscore');

module.exports = function (keys) {
    return {
        spuds: function (req, res) {
        	
            var breadcrumbs = [{ 'title' : 'SPUDS', 'href' : '/dashboard' }];
			
			krowdio.krowdioGetPostsForEntity(Parse.User.current(), req.headers['user-agent']).then(function(_spuds) {
				var spuds = JSON.parse(_spuds).items,
					Team = Parse.Object.extend('Team'),
	            	teamQuery = new Parse.Query(Team),
	            	updatedSpuds = [];
            	
				teamQuery.equalTo('admins', Parse.User.current());
            
            	teamQuery.find().then(function(teams) {
            		var promise = Parse.Promise.as();
            		
            		_.each(spuds, function(spud) {
            			var _spud = spud;
            			
            			promise = promise.then(function() {
            				var publisherFetchedPromise = new Parse.Promise(),
            					userQuery = new Parse.Query(Parse.User);
            					
            				userQuery.equalTo('krowdioUserId', _spud.user._id);
            				
            				userQuery.first().then(function(user) {
            					_spud.publisher = user;
            					updatedSpuds.push(_spud);
            					publisherFetchedPromise.resolve();
            				});
            				
            				return publisherFetchedPromise;
            			});
            		});
            		
            		promise.then(function() {
            			res.render('dashboard/spuds', {
			                'breadcrumbs' : breadcrumbs,
			                'spuds' : updatedSpuds,
			                'spudContainer' : require('cloud/commons/spudContainer'),
			                'teams' : teams
		            	});
            		});
            		
		            
	            });
			});
            	
        },

        mySpuds: function(req, res) {
        	var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/spuds' }, { 'title' : 'My Spuds', 'href' : '/dashboard/fans/spuds' }],
        		Team = Parse.Object.extend('Team'),
            	teamQuery = new Parse.Query(Team);
            	
			teamQuery.equalTo('admins', Parse.User.current());
            
            teamQuery.find().then(function(teams) {
	        	res.render('dashboard/fan/mySpuds', {
	                'breadcrumbs' : breadcrumbs,
	                'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() },
	                'teams' : teams
	            });
            });
        },
        
        myFavorites: function(req, res) {
        	var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/favorites' }, { 'title' : 'My Favorites', 'href' : '/dashboard/fans/favorites' }];
        	res.render('dashboard/fan/myFavorites', {
                'breadcrumbs' : breadcrumbs,
                'displayUsers' : require('cloud/commons/displayUsers'),
            });
        },
        
        basicInfo: function(req, res) {
        	var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/basicInfo' }, { 'title' : 'Basic Info', 'href' : '/dashboard/fans/basicInfo' }];
        	res.render('dashboard/fan/basicInfo', {
                'breadcrumbs' : breadcrumbs,
                'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
            });
        },
        
        settings: function(req, res) {
        	var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/settings' }, { 'title' : 'Settings', 'href' : '/dashboard/fans/settings' }];
        	res.render('dashboard/fan/settings', {
                'breadcrumbs' : breadcrumbs,
            });
        }
        
    };
};