module.exports = function (keys) {
    Parse.initialize(keys.getApplicationID(), keys.getJavaScriptKey());

	var krowdio = require('cloud/krowdio');

    return {
        login: function(req, res) {
            Parse.User.logIn(req.body.email, req.body.password, {
                success: function(user) {
                    res.send(200, '200');
                },
                error: function(user, error) {
                	console.log(error);
                	res.send(200, '' + error.code);
                }
            });
        },

        logout: function(req, res) {
            Parse.User.logOut();
            res.redirect('/');
        },
        
        register: function(req, res) {
        	var email = req.body.email,
        		password1 = req.body.password1,
        		password2 = req.body.password2;
        		
        	if (Parse.User.current()) {
        		Parse.User.logOut();
        	}	
        	
        	if (email == "") {
        		res.send(200, '0');
    		}
	        else if (password1 == "" && password2 == "") {
	            res.send(200, '1');
	        }
	        else if (password1 > "" && password1 != password2) {
	            res.send(200, '2');
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
        			res.send(200, '200');
        		}, function(error) {
        			console.log(error);
        			res.send(200, '' + error.code);
        		});

    		}
        },
        
        editProfile: function(req, res) {
        	var name = req.body.name, freeText = req.body.freeText;
        	
        	var user = Parse.User.current();
        	user.set('nickname', req.body.nickname);
	        user.set('name', name);
	        user.set('lastName', req.body.lastName);
	        user.set('nameSearch', req.body.name.toLowerCase());
	        user.set('freeText', freeText);
	        user.set('email', req.body.email);
	        user.set('phone', req.body.phone);
	        user.set('facebook', req.body.facebook);
	        user.set('googlePlus', req.body.googlePlus);
	        user.set('twitter', req.body.twitter);
	        
	        var	dob = req.body.dateOfBirth.split('-').reverse().join('-');
	        
        	user.set('dob', dob);
        	
    		user.set('profileImageThumb', req.body.avatarId);

    		user.save()
            .then(function(){
            	krowdio.krowdioUploadProfilePicture(user, req.body.avatarId);
                res.redirect('/dashboard/fans/basicInfo');
            });
        }
        
    };
};