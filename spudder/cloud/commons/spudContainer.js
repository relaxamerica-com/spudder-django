var EJS = require('ejs');
var fs = require('fs');
var utils = require('cloud/utilities')();

module.exports = function(spud, isMentions, getValueOrEmpty, user) {
	if (isMentions && spud.target.objectType == 'image') { // workaround for image url from krowd.io until they fix the serving url
		spud.target.image.url = spud.target.image.url.replace('_t', '_r');
	}
	
	var data = { 
			'spud' : spud, 
			'getValueOrEmpty' : getValueOrEmpty, 
			'user' : user,
			'convertDate' : utils.convertDate
		},
		template = isMentions ? 'spudContainerMentions.ejs' : 'spudContainer.ejs',
		html = EJS.render(fs.readFileSync('cloud/views/commons/' + template), data);
	
	return html;
};