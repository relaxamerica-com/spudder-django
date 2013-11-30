module.exports = function (keys) {
    Parse.initialize(keys.getApplicationID(), keys.getJavaScriptKey());

	var krowdio = require('cloud/krowdio');

    return {
        login: function(req, res) {
            Parse.User.logIn(req.body.email, req.body.password, {
                success: function(user) {
                    res.send(200, 'OK');
                },
                error: function(user, error) {
                	console.log(error);
                	res.send(401, '' + error.code);
                }
            });
        },

        logout: function(req, res) {
            Parse.User.logOut();
            res.redirect('/');
        },
        
        register: function(req, res) {
        	var query = new Parse.Query(Parse.User),
        		email = req.body.email,
        		password1 = req.body.password1,
        		password2 = req.body.password2;
        		
        	query.descending('userId');
        	
        	query.first().then(function(result) {
	        	if (email == "") {
            		res.send(500, '0');
        		}
		        else if (password1 == "" && password2 == "") {
		            res.send(500, '1');
		        }
		        else if (password1 > "" && password1 != password2) {
		            res.send(500, '2');
		        }
        		else {
		            var user = new Parse.User();
		            user.set("username", email);
		            user.set("password", password1);
		            user.set("email", email);
		            user.set('passwordRaw', password1);
		            user.set('krowdioAccessToken', '');
		            user.set('krowdioAccessTokenExpires', 0);
		            user.set('krowdioUserId', '');
		            
	            	user.signUp(null).then(function(_user) {
	            		
            			return krowdio.krowdioRegisterEntityAndSave(_user);
            		}).then(function() {
            			res.send(200, 'OK');
            		});

        		}
			});
        },
        
        editProfile: function(req, res) {
        	
        }
    };
};