var krowdio = require('cloud/krowdio');

module.exports = function (keys) {
	return {
		createSpud: function(req, res) {
			var spudData = { 'title': req.body.title, 'usertext' : req.body.title }; 
				
			krowdio.krowdioPost(Parse.User.current(), spudData, req.headers['user-agent']).then(function() {
				res.redirect('/dashboard');
			});
			
		}
	};
};