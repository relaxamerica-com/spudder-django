exports.login = function(req, res) {
<<<<<<< HEAD
	Parse.initialize('RwjN7ubrqVZSXcwd2AWaQtov6Mgsi7hAXZ510xTR', 'zDk1PxddnEJwnLKxrnypGuM4pIq9Z7adAi4rprgH');

	Parse.User.logIn(req.body.username, req.body.password, {
		success: function(user) {
=======
//	Parse.initialize('RwjN7ubrqVZSXcwd2AWaQtov6Mgsi7hAXZ510xTR', 'zDk1PxddnEJwnLKxrnypGuM4pIq9Z7adAi4rprgH');

	Parse.User.logIn(req.body.username, req.body.password, {
		success: function(user) {
			console.log(user);
>>>>>>> parse
			res.redirect('/');
		},
		error: function(user, error) {
			console.log('error occured');
		}
	});
<<<<<<< HEAD
=======
};

exports.logout = function(req, res) {
	Parse.User.logOut();
	res.redirect('/');
>>>>>>> parse
};