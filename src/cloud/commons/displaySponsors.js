var EJS = require('ejs');
var fs = require('fs');

module.exports = function(id, title, sponsors) {
    console.log('Sponsors count: ' + sponsors.length);

    return EJS.render(fs.readFileSync('cloud/views/commons/displaySponsors.ejs'), {
        'id' : id, 'title' : title, 'sponsors' : sponsors
    });
};