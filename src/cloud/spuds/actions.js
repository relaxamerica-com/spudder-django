var krowdio = require('cloud/krowdio');

module.exports = function (keys) {
	return {
		createSpud: function(req, res) {
			var url = req.body.image,
				userAgent = req.headers['user-agent'],
				videoURL = req.body.video,
				imageLoadedPromise = new Parse.Promise(),
				spudData = { 'title': req.body.title || videoURL, 'usertext' : req.body.tags, 'type' : videoURL.length > 0 ? 'video' : 'text' };
				
			if (url.length == 0) {
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
		}
	};
};