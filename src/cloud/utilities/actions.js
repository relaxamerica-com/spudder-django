module.exports = function (keys) {
	
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
    	}
    };
};