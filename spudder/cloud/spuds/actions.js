var krowdio = require('cloud/krowdio'),
	_ = require('underscore');

module.exports = function (keys) {
	return {
		createSpud: function(req, res) {
			var url = req.body.image,
				userAgent = req.headers['user-agent'],
				videoURL = req.body.video,
				imageLoadedPromise = new Parse.Promise(),
				isVideo = videoURL.length > 0,
				spudData = { 'title': req.body.title, 'usertext' : req.body.tags, 'type' : isVideo ? 'video' : 'text' };
			
			if (isVideo) {
				spudData.text = videoURL;
			}
			
			if (url.length == 0 || isVideo) {
				imageLoadedPromise.resolve();
			} else {
				krowdio.krowdioUploadMedia(Parse.User.current(), url, userAgent).then(function(imageData) {
					spudData.media = imageData.data._id;
					spudData.type = 'image';
					imageLoadedPromise.resolve();
						
				});
			}
				
			
			imageLoadedPromise.then(function() {
				krowdio.krowdioPost(Parse.User.current(), spudData, userAgent).then(function() {
					res.redirect('/dashboard');
				});
			});
		},
		
		comment: function(req, res) {
			var id = req.params.id,
				userAgent = req.headers['user-agent'],
				text = req.body.comment;
				
			krowdio.krowdioPostComment(userAgent, id, text).then(function(response) {
				res.send('200', response);
			});
			
		},
		
		encodeTags: function(req, res) {
			var tags = req.body.tags.split(' '),
				promise = Parse.Promise.as(),
				encodedTags = [];
			
			_.each(tags, function(tag) {
				
				promise = promise.then(function() {
					var clazzMatch = tag.match(/(Team|Coach|Player|User){1}/g),
						id = tag.replace(new RegExp('@' + clazzMatch), ''),
						getPromise = new Parse.Promise();
					
					var EntityClass = Parse.Object.extend(clazzMatch[0]),
						query = new Parse.Query(EntityClass);
					
					query.get(id).then(function(entity) {
						encodedTags.push({
							id: entity.id,
							name: entity.get('name'),
							clazz: clazzMatch[0]
						});
						getPromise.resolve();
					}, function(error) {
						getPromise.resolve();
					});
					
					return getPromise;
				});
				
			});
			
			promise.then(function() {
				res.send('200', JSON.stringify({ items: encodedTags }));
			});
		},
		
		addTag: function(req, res) {
			
		},
		
		toggleLike: function(req, res) {
			var id = req.body.id,
				userAgent = req.headers['user-agent'];
				
			krowdio.krowdioToggleLike(userAgent, id).then(function(likes) {
				res.send('200', likes);
			});
		},
		
		getCommentsPublishers: function(req, res) {
			var promise = Parse.Promise.as(),
				ids = req.body.ids,
				items = {};
            		
    		_.each(ids, function(krowdioUserId) {
    			promise = promise.then(function() {
    				var publisherFetchedPromise = new Parse.Promise(),
    					userQuery = new Parse.Query(Parse.User);
    				
    				userQuery.equalTo('krowdioUserId', krowdioUserId);
    				
    				userQuery.first().then(function(user) {
    					items[krowdioUserId] = user;
    					publisherFetchedPromise.resolve();
    				});
    				
    				return publisherFetchedPromise;
    			});
    		});
    		
    		promise.then(function() {
    			res.send('200', JSON.stringify({ 'items' : items }));
    		});
		},
		
		getComments: function(req, res) {
			var spudId = req.query.spudId,
				userAgent = req.headers['user-agent'];
			
			krowdio.krowdioGetCommentsForPost(userAgent, spudId).then(function(comments) {
				var _comments = JSON.parse(comments).data,
					promise = Parse.Promise.as(),
					idUserMapping = {};
            	
	    		_.each(_comments, function(comment) {
	    			promise = promise.then(function() {
	    				var publisherFetchedPromise = new Parse.Promise(),
	    					userQuery = new Parse.Query(Parse.User),
	    					id = comment.from.username.replace('User', '');
	    				
	    				if (id in idUserMapping) {
		    				comment.publisher = idUserMapping[id];
	    					publisherFetchedPromise.resolve();
	    				} else {
	    					userQuery.get(id).then(function(user) {
		    					comment.publisher = user;
		    					idUserMapping[id] = user;
		    					publisherFetchedPromise.resolve();
		    				});
	    				}
	    				
	    				return publisherFetchedPromise;
	    			});
	    		});
				
				promise.then(function() {
					res.send('200', JSON.stringify(_comments));
				});
			});
		},

        getLikes: function(req, res) {
            var spudId = req.query.spudId,
                userAgent = req.headers['user-agent'];

            krowdio.krowdioGetLikesForPost(userAgent, spudId).then(function(likes) {
                res.send('200', likes);
            });
        }
	};
};