var EJS = require('ejs');
var fs = require('fs');

module.exports = function(id, title, isSponsorUs) {
	var data = { 'id' : id, 'title' : title, 'isSponsorUs' : isSponsorUs };
	var html = EJS.render(fs.readFileSync('cloud/views/commons/displayItems.ejs'), data);
	
	return html;
};