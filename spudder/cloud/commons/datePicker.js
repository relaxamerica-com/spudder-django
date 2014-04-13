var EJS = require('ejs');
var fs = require('fs');

module.exports = function(inputName, defaultDate) {
	var data = { 'inputName' : inputName, 'defaultDate' : defaultDate };
	var html = EJS.render(fs.readFileSync('cloud/views/commons/datePicker.ejs'), data);
	
	return html;
};