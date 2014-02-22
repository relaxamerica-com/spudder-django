module.exports = function() {
	var self = this,
		_ = require('underscore'),
		keys = require('cloud/keys.js')(),
		mandrill = require('mandrill'),
		utilities = require('cloud/utilities')();
	
	this.sendInvitation = function(email, invitation, template, userName, singleEmailPromise) {
		invitation.save(null).then(function(_entityInv) {
			var name = userName,
				prefixURL = 'https://' + keys.getAppName() + '.parseapp.com';
				acceptURL = prefixURL +'/acceptEntityInvitation/' + _entityInv.id,
				rejectURL = prefixURL + '/rejectEntityInvitation/' + _entityInv.id,
				listURL = prefixURL + '/invitationsList',
				isUnregistered = name == email,
				signUpURL = isUnregistered ? prefixURL + '?acceptInvitation=' + _entityInv.id + '&email=' + email.replace('@', '%40') + '#mySignup' : '';
				text = utilities.renderEmail(template, { 
	    				'name' : name,
	    				'signUpURL' : signUpURL,
	    				'acceptURL' : acceptURL,
	    				'rejectURL' : rejectURL,
	    				'entityType' : _entityInv.get('entityType'),
	    				'listURL' : listURL,
	    				'entityName' : _entityInv.get('entityName')
					});
			
			mandrill.initialize(keys.MANDRILL_API_KEY);
			mandrill.sendEmail({
				message: {
			    	html: text,
				    subject: "You have been invited to become an admin of " + _entityInv.get('entityType') + ': ' + _entityInv.get('entityName'),
				    from_email: "help@spudder.com",
				    from_name: "Spudder.com",
			    	to: [{
					        email: email,
					        name: name
			      		}]
		  		},
		  		async: true
			}, {
				success: function(res) {
	        		singleEmailPromise.resolve();
				},
				error: function(res) {
					console.log(res);
				}
			});
		});
	};
	
	return {
		addAdmins: function(entity, adminsEmailsList, notFoundEmails) {
			var promise = Parse.Promise.as();
			
			_.each(adminsEmailsList, function(adminEmail) {
				promise = promise.then(function() {
					var singleEmailPromise = new Parse.Promise(),
						_adminEmail = adminEmail;
					
	    			new Parse.Query(Parse.User).equalTo('email', adminEmail).first().then(function(user) {
	    				var EntityInvitation = Parse.Object.extend('EntityInvitation'),
			    			entityInv = new EntityInvitation(),
			    			entityType = entity.className;
			    		
			    		entityInv.set('entityName', entity.get('name'));
			    		entityInv.set('entityType', entityType);
			    		entityInv.set('entityId', entity.id);
			    		entityInv.set('inviting', Parse.User.current());
			    		entityInv.set('invitedEmail', adminEmail);
			    			
	    				if (user === null || user === undefined) {
	    					self.sendInvitation(_adminEmail, entityInv, 'cloud/views/emails/inviteUnregistered.ejs', _adminEmail, singleEmailPromise);
	    				} else {
	    					entityInv.set('invited', user);
	    					self.sendInvitation(_adminEmail, entityInv, 'cloud/views/emails/inviteRegistered.ejs', user.get('name'), singleEmailPromise);
	    				}
	    				
	    			});
	    			
	    			return singleEmailPromise;
				});
			});
	        		
			return promise;
	  },
	  
	  sendConfirmation: function(invitation, invited, inviting, isAccepted, promise) {
		  	var invitedName = invited.get('name') ? invited.get('name') : invited.getEmail(),
		  		text = utilities.renderEmail('cloud/views/emails/inviteConfirmation.ejs', { 
	    				'invitedName' : invitedName,
	    				'invitingName' : inviting.get('name'),
	    				'entityType' : invitation.get('entityType'),
	    				'entityName' : invitation.get('entityName'),
	    				'isAccepted' : isAccepted
					});
				
			mandrill.initialize(keys.MANDRILL_API_KEY);
			mandrill.sendEmail({
				message: {
			    	html: text,
				    subject: "User " + invitedName + (isAccepted ? ' has accepted ' : ' has rejected ') + 'the invitation',
				    from_email: "help@spudder.com",
				    from_name: "Spudder.com",
			    	to: [{
					        email: inviting.getEmail(),
					        name: inviting.get('name')
			      		}]
		  		},
		  		async: true
			}, {
				success: function(res) {
	        		promise.resolve();
				},
				error: function(res) {
					console.log(res);
				}
			});
	  	}
	};	   
};