var krowdioClientKey = "52769e9ff1f70e0552df58a4",
	krowdioGlobalPassword = "spudtastic";

//This is a massive hack as the krowdio login call causes a riderct that I can cannot correctly follow
//using the jQuery xhr promise
var currentAccessToken = null,
    setKrowdioUser = function(entity, responseText, promise) {
    	var krowdioData = JSON.parse(responseText);
    	if (krowdioData.error != null)
            return Parse.Promise.error(krowdioData);
        entity.set('krowdioAccessToken', krowdioData.access_token);
        entity.set('krowdioAccessTokenExpires', Math.round(new Date().getTime() / 1000) + krowdioData.expires_in);
        entity.set('krowdioUserId', krowdioData.user._id);
        entity.save(null, {
            success: function(_entity){
                promise.resolve(_entity);
            },
            error: function(error){
                promise.reject(error);
            }
        });
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
	
	return self._krowdidEnsureOAuthTokenForEntity(entity, userAgent);	
};
		
exports._krowdidEnsureOAuthTokenForEntity = function(entity, userAgent) {
    var expires = entity.get('krowdioAccessTokenExpires');
    
    if (Math.round(new Date().getTime() / 1000) > (expires + 10)) {
    	
        var promise = new Parse.Promise(),
        	postData = {
            'client_id': krowdioClientKey,
            'email': entity.id + "@spudder.com",
            'password': krowdioGlobalPassword
        };
        
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
            
            console.log(postData)
            
            Parse.Cloud.httpRequest({
                url: "http://api.krowd.io/post",
                body: postData,
                method: 'POST',
                headers: { 'Authorization' : token },
	            success: function(httpResponse) {
	            	console.log(httpResponse.text)
	            	console.log('success')
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
		
exports.krowdioGetPostsForEntity = function(entity, userAgent){
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
            console.log(userAgent)
            return Parse.Promise.as(krowdioData.text);
        },
        function(krowdioData){
            if (typeof krowdioData === "string")
                krowdioData = JSON.parse(krowdioData);
            return Parse.Promise.error(krowdioData);
    	});
    	
};
		
exports.krowdioUploadProfilePicture = function(entity, dataUri){
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
		
exports.krowdidGetPopularStream = function(userAgent){
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