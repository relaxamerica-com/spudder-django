module.exports = function (app) {
    var home = require('cloud/home/actions');
    app.get('/', home.home);

    var tournament = require('cloud/tournament/actions');
    app.get('/tournament', tournament.view);

    var spudmart = require('cloud/spudmart/actions');
    app.get('/spudmart', spudmart.view);
    app.get('/spudmart/offer', spudmart.offer);

    var teams = require('cloud/teams/actions');
    app.get('/teams/:teamID', teams.view);
    app.get('/teams/:teamID/offers/:offerID', teams.offer);
};