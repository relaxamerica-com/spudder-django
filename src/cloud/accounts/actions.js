module.exports = function (keys) {
    Parse.initialize(keys.getApplicationID(), keys.getJavaScriptKey());

    return {
        login: function(req, res) {
            Parse.User.logIn(req.body.email, req.body.password, {
                success: function(user) {
                    res.redirect('/dashboard');
                },
                error: function(user, error) {
                    console.log(error);
                }
            });
        },

        logout: function(req, res) {
            Parse.User.logOut();
            res.redirect('/');
        },
        
        register: function(req, res) {
        	var query = new Parse.Query(Parse.User);
        	query.descending('userId');
        	
        	query.first().then(function(result) {
	        	if ( req.body.password1 == req.body.password2 ) {
		        	Parse.User.signUp(req.body.email, req.body.password1, { 'userId' : result.get('userId') + 1 }, {
		        		success: function(user) {
		        			console.log('success');
		                    res.redirect('/');
		                },
		                error: function(user, error) {
		                    console.log(error);
		                }
		        	});
	        	} else {
	        		console.log('error');
	        	}
			});
        }
    };
};