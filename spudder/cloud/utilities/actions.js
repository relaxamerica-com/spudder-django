module.exports = function (keys) {
	var krowdio = require('cloud/krowdio');
	
    return {
    	checkEmailsExists: function(req, res){
    		var notFoundEmails = [],
    			emails = req.query.emails.replace(/\s+/, '').split(',').filter(function(el) { return el.length != 0; }),
    			_ = require('underscore'),
    			promise = Parse.Promise.as();
    		
    		_.each(emails, function(email) {
				promise = promise.then(function() {
					var queryPromise = new Parse.Promise();
					
	    			new Parse.Query(Parse.User).equalTo('email', email).first().then(function(user) {
	    				if (user === null || user === undefined) {
	    					notFoundEmails.push( email );
	    				}
	    				queryPromise.resolve();
	    			});
	    			
	    			return queryPromise;
				});
			});
	        		
			promise.then(function() {
				var obj = {
					'notFoundEmails' : notFoundEmails
				};
				res.send('200', JSON.stringify(obj) );
			});
    	},
    	
    	getTeamIdByName: function(req, res) {
        	var name = req.query.name,
        		Team = Parse.Object.extend('Team'),
        		query = new Parse.Query(Team);
        		
        	query.equalTo('name', name);
        		
        	query.first().then(function(entity) {
        		if (entity == null || entity == undefined) {
        			res.send('200',
        				JSON.stringify({ 'exists' : false })
         			);
        			return;
        		}
        		
        		res.send('200',
    				JSON.stringify({ 'exists' : true, 'id' : entity.id })
     			);
        	});
       },
       
       getTeamPlayersAndCoaches: function(req, res) {
       		var teamId = req.query.id,
       			Team = Parse.Object.extend('Team'),
       			query = new Parse.Query(Team);
       			
       		query.get(teamId).then(function(team) {
       			var Player = Parse.Object.extend('Player'),
       				queryPlayer = new Parse.Query(Player),
       				Coach = Parse.Object.extend('Coach'),
       				queryCoach = new Parse.Query(Coach);
       			
       			queryCoach.equalTo('team', team);
       			queryPlayer.equalTo('team', team);
       			
       			Parse.Promise.when([queryCoach.find(), queryPlayer.find()]).then(function(coaches, players) {
       				res.send('200',
    					JSON.stringify({ 'players' : players, 'coaches' : coaches })
     				);
       			});
       		});
       },
       
       fixDb: function(req, res) {
       		var Team = Parse.Object.extend('Coach'),
       			query = new Parse.Query(Team),
       			_ = require('underscore');
       		
       		query.equalTo('krowdioUserId', undefined);
       		console.log('fixing')
       		query.find().then(function(teams) {
       			console.log(teams)
       			var promise = Parse.Promise.as();
       			
       			_.each(teams, function(team) {
       				
			    	promise = promise.then(function() {
			    		return krowdio.krowdioRegisterEntityAndSave(team);
		    		});
			  	});
			  	
				return promise;
       		}).then(function() {
       			res.redirect('/');
       		});
       }
    };
};