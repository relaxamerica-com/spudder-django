var EJS = require('ejs');
var fs = require('fs');

module.exports = function(users, orientation, maxUsers) {
	var data = { 'users' : users.splice(0, maxUsers), 'orientation' : orientation, 'maxUsers' : maxUsers };
	var html = EJS.render(fs.readFileSync('cloud/views/commons/displayUsers.ejs'), data);
	
	return html;
};