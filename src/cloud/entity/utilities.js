module.exports = function() {
	return {
		addAdmins: function(entity, adminsEmailsList, notFoundEmails) {
			var promise = Parse.Promise.as(),
				_ = require('underscore'),
				keys = require('cloud/keys.js')(),
				mandrill = require('mandrill'),
				utilities = require('cloud/utilities')();
			
			_.each(adminsEmailsList, function(adminEmail) {
				promise = promise.then(function() {
					var finalPromise = new Parse.Promise();
					
	    			new Parse.Query(Parse.User).equalTo('email', adminEmail).first().then(function(user) {
	    				console.log(user);
	    				if (user === null || user === undefined) {
	    					finalPromise.resolve();
	    				}
	    				
	    				var EntityInvitation = Parse.Object.extend('EntityInvitation'),
			    			entityInv = new EntityInvitation(),
			    			entityType = entity.className,
			    			_user = user;
			    			
			    		entityInv.set('entityName', entity.get('name'));
			    		entityInv.set('entityType', entityType);
			    		entityInv.set('entityId', entity.id);
			    		entityInv.set('inviting', Parse.User.current());
			    		entityInv.set('invited', user);
			    		
			        	entityInv.save(null).then(function(_entityInv) {
			        		console.log(_entityInv);
			        		var acceptURL = 'https://' + keys.getAppName() +'.parseapp.com/acceptEntityInvitation/' + _entityInv.id,
			        			rejectURL = 'https://' + keys.getAppName() +'.parseapp.com/acceptEntityInvitation/' + _entityInv.id,
			        			listURL = 'https://' + keys.getAppName() + '.parseapp.com/invitationsList',
			        			text = utilities.renderEmail('cloud/views/emails/inviteEntity.ejs', { 
			            				'name' : _user.get('name'),
			            				'acceptURL' : acceptURL,
			            				'rejectURL' : rejectURL,
			            				'entityType' : entityType,
			            				'listURL' : listURL,
			            				'entityName' : _entityInv.get('entityName')
			        				});
			        		
							mandrill.initialize(keys.MANDRILL_API_KEY);
			        		mandrill.sendEmail({
								message: {
							    	html: text,
								    subject: "You have been invited to become an admin of " + entity.className + ': ' + _entityInv.get('entityName'),
								    from_email: "help@spudder.com",
								    from_name: "Spudder.com",
							    	to: [{
									        email: user.getEmail(),
									        name: user.get('name')
							      		}]
						  		},
						  		async: true
							}, {
								success: function(res) {
			                		finalPromise.resolve();
								},
								error: function(res) {
									console.log(res);
								}
							});
			        	});
	    			});
	    			
	    			return finalPromise;
				});
			});
	        		
			return promise;
	   }
	};	   
};