var EJS = require('ejs');
var fs = require('fs');

module.exports = function(spudmartBaseURL, isSoldOut, teamID, offerID) {
    return EJS.render(fs.readFileSync('cloud/views/teams/commons/donateButton.ejs'), {
        'spudmartBaseURL': spudmartBaseURL,
        'isSoldOut': isSoldOut,
        'teamID': teamID,
        'offerID': offerID
    });
};