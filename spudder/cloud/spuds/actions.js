var krowdio = require('cloud/krowdio');

module.exports = function (keys) {
	return {
		createSpud: function(req, res) {
			console.log(req.body)
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
		}
	};
};