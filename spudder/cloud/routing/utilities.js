module.exports = function (app, keys) {
    var utilities = require('cloud/utilities/actions')(keys),
    	helpers = require('cloud/routing/helpers')();

    app.get('/checkEmailsExists', utilities.checkEmailsExists);
    app.get('/getTeamIdByName', utilities.getTeamIdByName);
    app.get('/getTeamPlayersAndCoaches', utilities.getTeamPlayersAndCoaches);
    app.get('/fixDb', utilities.fixDb);
};