module.exports = function (app, keys) {
    var home = require('cloud/home/actions');
    app.get('/', home.home);

    var tournament = require('cloud/tournament/actions');
    app.get('/tournament', tournament.view);

    var teams = require('cloud/teams/actions')(keys);
    app.get('/teams/:teamID', teams.view);

    var offers = require('cloud/teams/offers')(keys);
    app.get('/teams/:teamID/offers/:offerID', offers.view);
    app.get('/teams/:teamID/offers', offers.list);

    var sponsors = require('cloud/sponsors/actions')(keys);
    app.get('/sponsors/:id', sponsors.view);

    var entity = require('cloud/entity/actions')(keys);
    app.get('/public/fan/:id', entity.fanPublicView);
    app.get('/public/:entityType/:id', entity.view);
};