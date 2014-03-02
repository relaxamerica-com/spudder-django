var EJS = require('ejs');
var fs = require('fs');

module.exports = function(id, title, teams) {
    return EJS.render(fs.readFileSync('cloud/views/commons/displayTeams.ejs'), {
        'id' : id, 'title' : title, 'teams' : teams
    });
};