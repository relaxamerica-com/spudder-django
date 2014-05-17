module.exports = function (keys) {
    Parse.initialize(keys.getApplicationID(), keys.getJavaScriptKey());

    var krowdio = require('cloud/krowdio'),
    	utils = require('cloud/utilities')();

    function decodeReturnURL(returnURL) {
        return returnURL ? returnURL.replace(encodeURIComponent('#'), '#'): undefined;
    }

    function handleAmazonError(httpResponse, response, template) {
        var jsonResponse = JSON.parse(httpResponse.text);

        console.error('Request failed with response code ' + httpResponse.status);
        console.error(jsonResponse.error + ' -> ' + jsonResponse.error_description);

        response.render(template, {
            'error': jsonResponse.error_description
        });
    }

    function handleRegisterError(params, error, res) {
        var messages = {
            '-1': 'Opps, something went wrong, please try again.',
            '125': "Email invalid",
            '202': 'Email already taken.'
        };
        params['error'] = messages[error.code];
        console.log(error);
        res.render('accounts/register', params);
    }

    function signUpUser(user, response, params) {
        user.signUp(null).then(function (_user) {
            return krowdio.krowdioRegisterEntityAndSave(_user);
        }).then(function () {
            response.redirect(params.returnURL ? params.returnURL : '/dashboard');
        }, function (error) {
            handleRegisterError(params, error, response);
        });
    }

    return {
        login: {
            get: function (req, res) {
                res.render('accounts/login', {
                    returnURL: decodeReturnURL(req.query.returnURL)
                });
            },

            post: function(req, res) {
                var params = {
                    email: req.body.email,
                    password: req.body.password,
                    error: undefined
                }, returnURL = req.body.returnURL;

                Parse.User.logIn(req.body.email, req.body.password, {
                    success: function() {
                        res.redirect(returnURL ? returnURL : '/dashboard');
                    },
                    error: function(user, error) {
                        params['error'] = error.message;
                        console.log(error);
                        res.render('accounts/login', params);
                    }
                });
            }
        },

        login_with_amazon: function (req, res) {
            var query = req.query,
                accessToken = query.access_token,
                error = query.error,
                params = {
                    email: '',
                    password1: '',
                    password2: '',
                    error: undefined,
                    returnURL: decodeReturnURL(req.query.returnURL)
                };

            if (error) {
                res.render('accounts/login', {
                    'error': query.error_description + '<br><a href="' + query.error_uri + '">Learn more</a>'
                });
            }

            Parse.Cloud.httpRequest({
                url: 'https://api.amazon.com/auth/O2/tokeninfo?access_token=' + encodeURIComponent(accessToken),
                success: function(httpResponse) {
                    var jsonResponse = JSON.parse(httpResponse.text),
                        isVerified = (jsonResponse.aud == keys.getLoginWithAmazonClientID());

                    if (!isVerified) {
                        res.render('accounts/login', {
                            error: 'Verification failed! Please contact administrators'
                        });
                    }

                    Parse.Cloud.httpRequest({
                        url: 'https://api.amazon.com/user/profile?access_token=' + encodeURIComponent(accessToken),
                        success: function (httpResponse) {
                            var jsonResponse = JSON.parse(httpResponse.text),
                                userQuery = new Parse.Query(Parse.User);

                            userQuery.equalTo('amazonID', jsonResponse.user_id);

                            userQuery.first({
                                success: function (_user) {
                                    if (_user == undefined) {
                                        params['error'] = 'No user registered with this Amazon account. <a href="/accounts/register">Please register first</a>';
                                        res.render('accounts/login', params);
                                        return;
                                    }

                                    Parse.User.logIn(_user.get('email'), _user.get('passwordRaw'), {
                                        success: function () {
                                            res.redirect(params.returnURL ? params.returnURL : '/dashboard');
                                        },
                                        error: function (user, error) {
                                            params['error'] = error.message;
                                            console.log(error);
                                            res.render('accounts/login', params);
                                        }
                                    });
                                },
                                error: function (error) {
                                    params['error'] = error.message;
                                    console.log(error);
                                    res.render('accounts/login', params);
                                }
                            });


                        },
                        error: function (httpResponse) {
                            handleAmazonError(httpResponse, res, 'accounts/login');
                        }
                    });
                },
                error: function(httpResponse) {
                    handleAmazonError(httpResponse, res, 'accounts/login');
                }
            });
        },

        logout: function(req, res) {
            Parse.User.logOut();
            res.redirect('/');
        },

        register: {
            get: function(req, res) {
                res.render('accounts/register', {
                    email: '',
                    password1: '',
                    password2: '',
                    error: undefined,
                    returnURL: decodeReturnURL(req.query.returnURL)
                });
            },

            post: function(req, res) {
                var params = {
                    email: req.body.email,
                    password1: req.body.password1,
                    password2: req.body.password2,
                    error: undefined,
                    returnURL: req.body.returnURL
                };

                if (Parse.User.current()) {
                    Parse.User.logOut();
                }

                if (params.email == "") {
                    params['error'] = "Email address is required!";
                } else if (params.password1 == "" && params.password2 == "") {
                    params['error'] = "Password and password confirmation are required!";
                } else if (params.password1 > "" && params.password1 != params.password2) {
                    params['error'] = "The passwords you entered did not match!";
                }
                if (params['error']) {
                    res.render('accounts/register', params);
                } else {
                    var user = new Parse.User();
                    user.set("username", params.email);
                    user.set("password", params.password1);
                    user.set("email", params.email);
                    user.set('passwordRaw', params.password1);
                    user.set('krowdioAccessToken', '');
                    user.set('krowdioAccessTokenExpires', 0);
                    user.set('krowdioUserId', '');

                    signUpUser(user, res, params);
                }
            }
        },

        register_with_amazon: function (req, res) {
            var query = req.query,
                accessToken = query.access_token,
                error = query.error,
                params = {
                    email: '',
                    password1: '',
                    password2: '',
                    error: undefined,
                    returnURL: decodeReturnURL(req.query.returnURL)
                };

            if (error) {
                res.render('accounts/register', {
                    'error': query.error_description + '<br><a href="' + query.error_uri + '">Learn more</a>'
                });
            }

            Parse.Cloud.httpRequest({
                url: 'https://api.amazon.com/auth/O2/tokeninfo?access_token=' + encodeURIComponent(accessToken),
                success: function(httpResponse) {
                    var jsonResponse = JSON.parse(httpResponse.text),
                        isVerified = (jsonResponse.aud == keys.getLoginWithAmazonClientID());

                    if (!isVerified) {
                        res.render('accounts/register', {
                            error: 'Verification failed! Please contact administrators'
                        });
                    }

                    Parse.Cloud.httpRequest({
                        url: 'https://api.amazon.com/user/profile?access_token=' + encodeURIComponent(accessToken),
                        success: function (httpResponse) {
                            var jsonResponse = JSON.parse(httpResponse.text),
                                user = new Parse.User();

                            user.set("username", jsonResponse.email);
                            user.set("email", jsonResponse.email);
                            user.set('name', jsonResponse.name ? jsonResponse.name : ' Anonymous');
                            user.set("amazonID", jsonResponse.user_id);
                            user.set("amazonAccessToken", accessToken);
                            user.set("password", jsonResponse.user_id);
                            user.set('passwordRaw', jsonResponse.user_id);
                            user.set('krowdioAccessToken', '');
                            user.set('krowdioAccessTokenExpires', 0);
                            user.set('krowdioUserId', '');

                            signUpUser(user, res, params);
                        },
                        error: function (httpResponse) {
                            handleAmazonError(httpResponse, res, 'accounts/register');
                        }
                    });
                },
                error: function(httpResponse) {
                    handleAmazonError(httpResponse, res, 'accounts/register');
                }
            });
        },

        editProfile: function(req, res) {
            var name = req.body.name, freeText = req.body.freeText,
            	isImageUploaded = req.body.avatarId ? true : false;

            var user = Parse.User.current();
            user.set('nickname', req.body.nickname);
            user.set('name', name);
            user.set('lastName', req.body.lastName);
            user.set('nameSearch', req.body.name.toLowerCase());
            user.set('freeText', freeText);
            user.set('email', req.body.email);
            user.set('phone', req.body.phone);
            
            if (utils.isWebsite(req.body.facebook)) {
            	user.set('facebook', req.body.facebook);
            } else {
            	user.set('facebook', 'https://www.facebook.com/' + req.body.facebook);
            }
            if (utils.isWebsite(req.body.googlePlus)) {
	            user.set('googlePlus', req.body.googlePlus);
            } else {
            	user.set('googlePlus', 'https://plus.google.com/u/0/' + req.body.googlePlus);
            }
            if (utils.isWebsite(req.body.twitter)) {
	            user.set('twitter', req.body.twitter);
            } else {
            	user.set('twitter', 'http://www.twitter.com/' + req.body.twitter);
            }
            if (utils.isWebsite(req.body.instagram)) {
	            user.set('instagram', req.body.instagram);
            } else {
	            user.set('instagram', 'http://instagram.com/' + req.body.instagram);
            }

            var	dob = req.body.dateOfBirth.split('-').reverse().join('-');

            user.set('dob', dob);

			if (isImageUploaded) {
	            user.set('profileImageThumb', req.body.avatarId);
			}

            user.save()
            .then(function(){
            	if (isImageUploaded) {
	                krowdio.krowdioUploadProfilePicture(user, req.body.avatarId, req.headers['user-agent']).then(function() {
	                	res.redirect('/dashboard/fans/basicInfo');
	                });
            	}
                res.redirect('/dashboard/fans/basicInfo');
            });
        },
        
        loginOrRegister: function(req, res) {
        	res.render('accounts/loginOrRegister',
        	{
        		'next' : req.query.next
        	});
        }
    };
};