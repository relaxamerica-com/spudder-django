var EJS = require('ejs');
var fs = require('fs');

module.exports = function() {
    return EJS.render(fs.readFileSync('cloud/views/commons/share/googlePlus.ejs'));
};