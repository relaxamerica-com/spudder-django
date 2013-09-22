var EJS = require('ejs');
var fs = require('fs');

module.exports = function(id, title) {
	var data = { 'id' : id, 'title' : title };
	var html = EJS.render(fs.readFileSync('cloud/views/dashboard/fan/modals/modalTop.ejs'), data);
	
	return html;
};