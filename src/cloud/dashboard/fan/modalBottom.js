var EJS = require('ejs');
var fs = require('fs');

module.exports = function(buttons) {
	if (!buttons) {
		buttons = {
			'first' : {
				text: 'Back',
				value: '#'
			},
			'second' : {
				text: 'Next',
				value: '#'
			}
		};
	}
	
	var html = EJS.render(fs.readFileSync('cloud/views/dashboard/fan/modals/modalBottom.ejs'), { 'buttons' : buttons });
	
	return html;
};