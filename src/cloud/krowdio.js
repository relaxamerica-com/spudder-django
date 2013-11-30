var krowdioClientKey = "52769e9ff1f70e0552df58a4",
	krowdioGlobalPassword = "spudtastic";

//This is a massive hack as the krowdio login call causes a riderct that I can cannot correctly follow
//using the jQuery xhr promise
var currentAccessToken = null;

exports.krowdioRegisterEntityAndSave = function (entity) {
    var params = {
        'client_id': krowdioClientKey,
        'username': entity.className.replace('_', '') + entity.id,
        'email': entity.id + "@spudder.com",
        'password': krowdioGlobalPassword
    };
    
    function setKrowdioUser(responseText, promise) {
    	var krowdioData = JSON.parse(responseText);
    	if (krowdioData.error != null)
            return Parse.Promise.error(krowdioData);
        entity.set('krowdioAccessToken', krowdioData.access_token);
        entity.set('krowdioAccessTokenExpires', Math.round(new Date().getTime() / 1000) + krowdioData.expires_in);
        entity.set('krowdioUserId', krowdioData.user._id);
        entity.save(null, {
            success: function(entity){
                promise.resolve(entity);
            },
            error: function(error){
                promise.reject(error);
            }
        });
    }
    
    var promise = new Parse.Promise();
    Parse.Cloud.httpRequest({
    	method: 'POST',
    	url: 'http://auth.krowd.io/user/register',
    	body: params,
        success: function(httpResponse) {
            setKrowdioUser(httpResponse.text, promise);
    	},
    	error: function(httpResponse) {
    		if (httpResponse.status == 302) {
    			Parse.Cloud.httpRequest({
    				method: 'POST',
			    	url: httpResponse.headers.Location,
			    	headers: httpResponse.headers,
			    	success: function(response) {
            			setKrowdioUser(response.text, promise);
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
		
exports.krowdioEnsureOAuthToken = function(entity){
    if (entity.id == Parse.User.current().id)
        return new Parse.Query(Parse.User).get(entity.id)
            .then(function(entity){
                return _krowdidEnsureOAuthTokenForEntity(entity);
            });
    else
        return _krowdidEnsureOAuthTokenForEntity(entity);

};
		
exports._krowdidEnsureOAuthTokenForEntity = function(entity){
    var expires = entity.get('krowdioAccessTokenExpires');
    if (Math.round(new Date().getTime() / 1000) > (expires + 10)) {
        var promise = new Parse.Promise();
        var postData = {
            client_id: krowdioClientKey,
            email: entity.id + "@spudder.com",
            password: krowdioGlobalPassword
        };
        $.ajax({ url: 'http://auth.krowd.io/user/login', data: postData, type: 'POST'})
            .success(function(krowdioData){
                if ($.type(krowdioData) === "string")
                    krowdioData = JSON.parse(krowdioData);
                if (krowdioData.error != null)
                    promise.reject(krowdioData);
//                    return Parse.Promise.error(krowdioData);
                var access_token = krowdioData.access_token;
//                currentAccessToken = access_token;
                entity.set('krowdioAccessToken', access_token);
                entity.set('krowdioAccessTokenExpires', Math.round(new Date().getTime() / 1000) + krowdioData.expires_in);
                entity.set('krowdioUserId', krowdioData.user._id);
                promise.resolve(entity);
                entity.save(null);
            });
        return promise;
    }
    else {
        return Parse.Promise.as(entity);
//        currentAccessToken = entity.get('krowdioAccessToken');
    }
};
		
exports.krowdioUploadMedia = function(entity) {
    return krowdioEnsureOAuthToken(entity)
        .then(function(entity){
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"';
            return $.ajax({
                url: "http://api.krowd.io/add/media",
                data: { encode: 'base64', data: "data:image/jpeg;base64," + spudDataUri },
                type: 'POST',
                headers: {'Authorization':token }
            });
        });
};
		
exports.krowdioPost = function(entity, post_data){
    return krowdioEnsureOAuthToken(entity)
        .then(function(entity){
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"';
            return $.ajax({
                url: "http://api.krowd.io/post",
                data: post_data,
                type: 'POST',
                headers: {'Authorization':token }
            });
        });
};
		
exports.krowdioGetPost = function(id) {

};
		
exports.krowdioGetPostsForEntity = function(entity){
    return krowdioEnsureOAuthToken(entity)
        .then(function(entity){
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"';
            return $.ajax({
                url: "http://api.krowd.io/stream/" + entity.get('krowdioUserId') + "?limit=10&page=1&maxid=&paging=None",
                type: 'GET',
                headers: {'Authorization':token }
            });
        })
        .then(function(krowdioData){
            if ($.type(krowdioData) === "string")
                krowdioData = JSON.parse(krowdioData);
            if (krowdioData.error != null)
                return Parse.Pomise.error(krowdioData.error);
            return Parse.Promise.as(krowdioData);
        },
        function(krowdioData){
            if ($.type(krowdioData) === "string")
                krowdioData = JSON.parse(krowdioData);
            return Parse.Promise.error(krowdioData);
        });
};
		
exports.krowdioUploadProfilePicture = function(entity, dataUri){
    var promise = new Parse.Promise();
    krowdioEnsureOAuthToken(entity)
        .then(function(entity){
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"';
            var url = 'http://auth.krowd.io/user/update';
            var postData = {
                data: dataUri
            };
            $.ajax({url: url, data: postData, type:'POST', headers: {'Authorization':token }})
                .done(function(krowdioData){
                    if ($.type(krowdioData) === "string")
                        krowdioData = JSON.parse(krowdioData);
                    if (krowdioData.error != null)
                        promise.reject(krowdioData);
                    entity.set('profileImageThumb', krowdioData.profile_image);
                    entity.save(null, {
                        success: function(entity){
                            promise.resolve(entity);
                        },
                        error: function(error){
                            promise.reject(error);
                        }
                    });
                });
        });
    return promise;
};
		
exports.krowdidGetPopularStream = function(){
    return krowdioEnsureOAuthToken(Parse.User.current())
        .then(function(entity){
            var token = 'Token token="' + entity.get('krowdioAccessToken') + '"';
            return $.ajax({
                url: "http://api.krowd.io/stream/popular?limit=30&page=1&maxid=&paging=None",
                type: 'GET',
                headers: {'Authorization':token }
            });
        })
        .then(function(krowdioData){
            if ($.type(krowdioData) === "string")
                krowdioData = JSON.parse(krowdioData);
            if (krowdioData.error != null)
                return Parse.Pomise.error(krowdioData.error);
            return Parse.Promise.as(krowdioData);
        },
        function(krowdioData){
            if ($.type(krowdioData) === "string")
                krowdioData = JSON.parse(krowdioData);
            return Parse.Promise.error(krowdioData);
        });
};