var EJS = require('ejs');
var fs = require('fs');

module.exports = function(path) {
    return EJS.render(fs.readFileSync('cloud/views/commons/share/email.ejs'), {'path': '' + path });
};