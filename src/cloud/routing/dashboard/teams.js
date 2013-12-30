module.exports = function (app, keys) {
    var helpers = require('cloud/routing/helpers')();

    var teams = require('cloud/dashboard/teams/teams')(keys);
    app.get('/dashboard/teams', helpers.loginRequired, teams.list.get);
    app.get('/dashboard/teams/create', helpers.loginRequired, teams.create.get);
    app.post('/dashboard/teams/create', helpers.loginRequired, teams.create.post);
    app.get('/dashboard/teams/edit/:id', helpers.loginRequired, teams.edit.get);
    app.post('/dashboard/teams/edit', helpers.loginRequired, teams.edit.post);
    app.get('/dashboard/teams/remove/:id', helpers.loginRequired, teams.remove.get);

    var teamOffers = require('cloud/dashboard/teams/offers')(keys);
    app.get('/dashboard/teams/:id/offers', helpers.loginRequired, teamOffers.list.get);
    app.get('/dashboard/teams/:id/offers/create', helpers.loginRequired, teamOffers.create.get);
    app.post('/dashboard/teams/:id/offers/create', helpers.loginRequired, teamOffers.create.post);
    app.get('/dashboard/teams/:teamID/offers/:offerID/edit', helpers.loginRequired, teamOffers.edit.get);
    app.post('/dashboard/teams/:teamID/offers/:offerID/edit', helpers.loginRequired, teamOffers.edit.post);
    app.get('/dashboard/teams/:teamID/offers/:offerID/remove', helpers.loginRequired, teamOffers.remove.get);
    app.get('/dashboard/teams/:teamID/offers/:offerID/donations', helpers.loginRequired, teamOffers.donations.get);
};