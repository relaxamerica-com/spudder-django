module.exports = function () {
    return {
        trim: function (text) {
            return text.replace(/^\s+|\s+$/g, '');
        },
        
        fullTrim: function (text) {
        	return text.replace(/(?:(?:^|\n)\s+|\s+(?:$|\n))/g,'').replace(/\s+/g,' ');
        },
        
        removeSpaces: function (text) {
        	return text.replace(/\s+/g, '');
        },
        
        renderEmail: function (path, params) {
        	var EJS = require('ejs');
			var fs = require('fs');

		    return EJS.render(fs.readFileSync(path), params);
        },
        
        convertDate: function (date) {
        	return (date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear();
        }
    };
};