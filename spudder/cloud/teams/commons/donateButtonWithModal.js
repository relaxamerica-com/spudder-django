var EJS = require('ejs');
var fs = require('fs');

module.exports = function(isLoggedIn, isSoldOut, teamID, offerID) {
    return EJS.render(fs.readFileSync('cloud/views/teams/commons/donateButtonWithModal.ejs'), {
        'isLoggedIn': isLoggedIn,
        'isSoldOut': isSoldOut,
        'teamID': teamID,
        'offerID': offerID
    });
};