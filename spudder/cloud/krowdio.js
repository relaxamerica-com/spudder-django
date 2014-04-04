var krowdioClientKey = "52769e9ff1f70e0552df58a4",
	krowdioGlobalPassword = "spudtastic";

//This is a massive hack as the krowdio login call causes a riderct that I can cannot correctly follow
var currentAccessToken = null,
    setKrowdioUser = function(entity, responseText, promise) {
    	var krowdioData = JSON.parse(responseText);
    	if (krowdioData.error != null) {
            return Parse.Promise.error(krowdioData);
    	}
    	
    	console.log('setting')
    	
        entity.set('krowdioAccessToken', krowdioData.access_token);
        entity.set('krowdioAccessTokenExpires', Math.round(new Date().getTime() / 1000) + krowdioData.expires_in);
        entity.set('krowdioUserId', krowdioData.user._id);
        
    	if (Parse.User.current()) {
	        entity.save(null, {
	            success: function(_entity){
	            	console.log('save done');
	            	console.log(promise);
	                promise.resolve(_entity);
	            },
	            error: function(object, error) {
	            	console.log(error);
	                promise.reject(error);
	            }
	        });
    	} else {
    		promise.resolve(entity);
    	}
    };

exports.krowdioRegisterEntityAndSave = function (entity) {
    var params = {
        'client_id': krowdioClientKey,
        'username': entity.className.replace('_', '') + entity.id,
        'email': entity.id + "@spudder.com",
        'password': krowdioGlobalPassword
    };
    
    var promise = new Parse.Promise();
    Parse.Cloud.httpRequest({
    	method: 'POST',
    	url: 'http://auth.krowd.io/user/register',
    	body: params,
        success: function(httpResponse) {
            setKrowdioUser(entity, httpResponse.text, promise);
    	},
    	error: function(httpResponse) {
    		if (httpResponse.status == 302) {
    			Parse.Cloud.httpRequest({
    				method: 'POST',
			    	url: httpResponse.headers.Location,
			    	headers: httpResponse.headers,
			    	success: function(response) {
            			setKrowdioUser(entity, response.text, promise);
			    	},
			    	error: function(response) {
			    		promise.reject();
			    	}
    			});
    		} else {
				promise.reject();
    		}
    	}
    });
    
    return promise;
};
		
exports.krowdioEnsureOAuthToken = function(entity, userAgent){
	var self = this;
	
	return self._krowdioEnsureOAuthTokenForEntity(entity, userAgent);	
};
		
exports._krowdioEnsureOAuthTokenForEntity = function(entity, userAgent) {
    var expires = entity.get('krowdioAccessTokenExpires');
    
    if (Math.round(new Date().getTime() / 1000) > (expires + 10)) {
    	
        var promise = new Parse.Promise(),
        	postData = {
            'client_id': krowdioClientKey,
            'email': entity.id + "@spudder.com",
            'password': krowdioGlobalPassword
        };
        
        console.log('_krowdioEnsureOAuthToken')
        
        Parse.Cloud.httpRequest({
	    	method: 'POST',
	    	url: 'http://auth.krowd.io/user/login',
	    	body: postData,
	    	headers: {
	    		'User-Agent' : userAgent
	    	},
	        success: function(httpResponse) {
	        	setKrowdioUser(entity, httpResponse.text, promise);
	    	},
	    	error: function(httpResponse) {
	    		if (httpResponse.status == 302) {
	    			Parse.Cloud.httpRequest({
	    				method: 'POST',
				    	url: httpResponse.headers.Location,
				    	headers: httpResponse.headers,
				    	success: function(response) {
	            			setKrowdioUser(entity, response.text, promise);
				    	},
						error: function(response) {
				    		promise.reject();
				    	}
	    			});
	    		} else {
					promise.reject();
	    		}
	    	}
	   });
	   
       return promise;
	} else {
       return Parse.Promise.as(entity);
    }
};
		
exports.krowdioUploadMedia = function(entity, url, userAgent) {
	var self = this;
    return self.krowdioEnsureOAuthToken(entity, userAgent)
        .then(function(entity){
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"',
            	promise = new Parse.Promise();
            
            Parse.Cloud.httpRequest({
                url: "http://api.krowd.io/add/media",
                body: { encode: 'base64', url: url },
                method: 'POST',
                headers: { 'Authorization' : token },
                success: function(httpResponse) {
                	promise.resolve(httpResponse);
                },
                error: function(httpResponse) {
                	promise.reject();
                }
            });
            return promise;
        });
};
		
exports.krowdioPost = function(entity, post_data, userAgent){
	var self = this,
		postData = post_data;
		
    return self.krowdioEnsureOAuthToken(entity, userAgent)
        .then(function(entity){
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"',
            	promise = new Parse.Promise();
            
            Parse.Cloud.httpRequest({
                url: "http://api.krowd.io/post",
                body: postData,
                method: 'POST',
                headers: { 'Authorization' : token },
	            success: function(httpResponse) {
	            	promise.resolve(entity);
	            },
	            error: function(httpResponse) {
	            	promise.reject(entity);
	            }
            });
            
            return promise;
        });
};
		
exports.krowdioGetPost = function(id) {

};
		
exports.krowdioGetPostsForEntity = function(entity, userAgent) {
	var self = this;
		
    return self.krowdioEnsureOAuthToken(entity, userAgent)
        .then(function(entity){
        	
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"',
            	promise = new Parse.Promise();
            	
            Parse.Cloud.httpRequest({
                url: "http://api.krowd.io/stream/" + entity.get('krowdioUserId') + "?limit=10&page=1&maxid=&paging=None",
                method: 'GET',
                headers: { 'Authorization' : token },
           		success: function(httpResponse) {
            		promise.resolve(httpResponse);
            	}, 
            	error: function(httpResponse) {
            		promise.reject(httpResponse);	
            	}
        	});
        	
            return promise;
        })
        .then(function(krowdioData){
            if (typeof krowdioData === "string")
                krowdioData = JSON.parse(krowdioData);
            if (krowdioData.error != null)
                return Parse.Pomise.error(krowdioData.error);
            return Parse.Promise.as(krowdioData.text);
        },
        function(krowdioData){
            if (typeof krowdioData === "string")
                krowdioData = JSON.parse(krowdioData);
            return Parse.Promise.error(krowdioData);
    	});
    	
};
		
exports.krowdioUploadProfilePicture = function(entity, dataUri, userAgent){
    var promise = new Parse.Promise(),
    	self = this;
    self.krowdioEnsureOAuthToken(entity, userAgent)
        .then(function(entity){
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"';
            var postData = {
                data: dataUri
            };
            Parse.Cloud.httpRequest({
		    	method: 'POST',
		    	url: 'http://auth.krowd.io/user/update',
		    	body: postData,
		    	headers: { 'Authorization': token },
		        success: function(httpResponse) {
		        	console.log(httpResponse.code);
		        	// entity.set('profileImageThumb', krowdioData.profile_image);
                    // entity.save(null, {
                        // success: function(entity){
                            // promise.resolve(entity);
                        // },
                        // error: function(error){
                            // promise.reject(error);
                        // }
                    // });
		    	},
		    	error: function(httpResponse) {
		    		console.log(httpResponse.code);
		    	}
		   });
        });
        
    return promise;
};
		
exports.krowdioGetPopularStream = function(userAgent){
	var self = this;
	
    return self.krowdioEnsureOAuthToken(Parse.User.current(), userAgent)
        .then(function(entity){
        	
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"',
            	promise = new Parse.Promise();
            	
            Parse.Cloud.httpRequest({
		    	method: 'GET',
		    	url: 'http://api.krowd.io/stream/popular?limit=30&page=1&maxid=&paging=None',
		    	headers: { 'Authorization' : token },
		        success: function(httpResponse) {
		            promise.resolve(httpResponse);
		    	},
		    	error: function(httpResponse) {
		    		promise.reject(httpResponse);
		    	}
		    });
		    
		    return promise;
        })
        .then(function(krowdioData){
            if (typeof krowdioData == 'string') {
            	krowdioData = JSON.parse(krowdioData);
            }
            if (krowdioData.error != null)
                return Parse.Pomise.error(krowdioData.error);
            return Parse.Promise.as(krowdioData.text);
        },
        function(krowdioData){
            return Parse.Promise.error(JSON.parse(krowdioData));
        });
};

exports.krowdioGetUserMentionActivity = function(userAgent, entity) {
	var self = this,
		userId = entity.get('krowdioUserId');
	
	return self.krowdioEnsureOAuthToken(entity, userAgent)
        .then(function(entity){
        	
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"',
            	promise = new Parse.Promise();
            
            Parse.Cloud.httpRequest({
		    	method: 'GET',
		    	url: 'http://api.krowd.io/activity/mentions?userid=' + userId + '&limit=10&page=1&maxid=&paging=None',
		    	headers: { 'Authorization' : token },
		        success: function(httpResponse) {
		            promise.resolve(httpResponse);
		    	},
		    	error: function(httpResponse) {
		    		console.log(httpResponse);
		    		promise.reject(httpResponse);
		    	}
		    });
		    
		    return promise;
        })
        .then(function(krowdioData){
           	if (typeof krowdioData == 'string') {
            	krowdioData = JSON.parse(krowdioData);
            }
            if (krowdioData.error != null) {
            	console.log(krowdioData.error);
                return Parse.Pomise.error(krowdioData.error);
            }
            return Parse.Promise.as(krowdioData.text);
        },
        function(krowdioData) {
        	if (typeof krowdioData == 'string') {
            	krowdioData = JSON.parse(krowdioData);
            }
        	return Parse.Promise.error(krowdioData);
        });
	
};

exports.krowdioPostComment = function(userAgent, contentID, text) {
	var promise = new Parse.Promise(),
    	self = this,
    	_contentID = contentID,
    	_text = text;
    	
    self.krowdioEnsureOAuthToken(Parse.User.current(), userAgent)
        .then(function(entity){
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"';
            var postData = {
                text: _text
            };
            Parse.Cloud.httpRequest({
		    	method: 'POST',
		    	url: 'http://api.krowd.io/comment/' + _contentID,
		    	body: postData,
		    	headers: { 'Authorization': token },
		        success: function(httpResponse) {
		        	promise.resolve(httpResponse.text);
		    	},
		    	error: function(httpResponse) {
		    		console.log(httpResponse)
		    		console.log(httpResponse.code);
		    		promise.reject();
		    	}
		   });
        });
        
    return promise;
};

exports.krowdioToggleLike = function(userAgent, contentID) {
	var promise = new Parse.Promise(),
    	self = this,
    	_contentID = contentID;
    	
    self.krowdioEnsureOAuthToken(Parse.User.current(), userAgent)
        .then(function(entity){
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"';
            
            Parse.Cloud.httpRequest({
		    	method: 'POST',
		    	url: 'http://api.krowd.io/like/' + _contentID,
		    	headers: { 'Authorization': token },
		        success: function(httpResponse) {
		        	promise.resolve(httpResponse.text);
		    	},
		    	error: function(httpResponse) {
		    		console.log(httpResponse.text)
		    		promise.reject();
		    	}
		   });
        });
        
    return promise;
};

exports.getForPost = function(what, userAgent, postId, entity, page) {
    var self = this,
        _postId = postId;
       
    if (page == undefined) {
    	page = 1;
    }

    return self.krowdioEnsureOAuthToken(entity, userAgent)
        .then(function(entity){

            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"',
                promise = new Parse.Promise();

            Parse.Cloud.httpRequest({
                method: 'GET',
                url: 'http://api.krowd.io/' + what + '/' + _postId + '?limit=5&page=' + page + '&newpage=1&startid=&direction=None',
                headers: { 'Authorization' : token },
                success: function(httpResponse) {
                	console.log(httpResponse.text);
                    promise.resolve(httpResponse);
                },
                error: function(httpResponse) {
                	console.log(httpResponse.text);
                    promise.reject(httpResponse);
                }
            });

            return promise;
        })
        .then(function(krowdioData){
            if (typeof krowdioData == 'string') {
                krowdioData = JSON.parse(krowdioData);
            }
            if (krowdioData.error != null)
                return Parse.Pomise.error(krowdioData.error);
            return Parse.Promise.as(krowdioData.text);
        },
        function(krowdioData){
            console.log(krowdioData);
            return Parse.Promise.error(krowdioData);
        });

};

exports.krowdioGetCommentsForPost = function(userAgent, postId, entity, page) {
	return this.getForPost('comment', userAgent, postId, entity, page);
};

exports.krowdioGetLikesForPost = function(userAgent, postId, entity, page) {
    return this.getForPost('like', userAgent, postId, entity, page);
};


