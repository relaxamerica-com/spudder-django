var EJS = require('ejs');
var fs = require('fs');
var utils = require('cloud/utilities')();

module.exports = function(spud, isDisplayArrows, getValueOrEmpty, user) {
	var data = { 
			'spud' : spud, 
			'isDisplayArrows' : isDisplayArrows, 
			'getValueOrEmpty' : getValueOrEmpty, 
			'user' : user,
			'convertDate' : utils.convertDate
		},
		html = EJS.render(fs.readFileSync('cloud/views/commons/spudContainer.ejs'), data);
	
	return html;
};