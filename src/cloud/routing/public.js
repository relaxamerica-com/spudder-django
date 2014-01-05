module.exports = function (app, keys) {
    var home = require('cloud/home/actions');
    app.get('/', home.home);

    var tournament = require('cloud/tournament/actions');
    app.get('/tournament', tournament.view);

    var spudmart = require('cloud/spudmart/actions');
    app.get('/spudmart', spudmart.view);
    app.get('/spudmart/offer', spudmart.offer);

    var teams = require('cloud/teams/actions')(keys);
    app.get('/teams/:teamID', teams.view);

    var offers = require('cloud/teams/offers')(keys);
    app.get('/teams/:teamID/offers/:offerID', offers.view);
    app.get('/teams/:teamID/offers', offers.list);

    var entity = require('cloud/entity/actions')(keys);
    app.get('/public/:entityType/:id', entity.view);
};