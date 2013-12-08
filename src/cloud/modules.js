function loginRequired(req, res, next) {
    var currentUser = Parse.User.current();
    if (!currentUser) {
        res.redirect('/#mySignin');
    } else {
        return next();
    }
}

module.exports = function (app, keys) {
    var home = require('cloud/home/actions');
    app.get('/', home.home);

    var accounts = require('cloud/accounts/actions')(keys);
    app.post('/accounts/login', accounts.login);
    app.post('/accounts/register', accounts.register);
    app.get('/accounts/logout', accounts.logout);
    app.post('/accounts/editProfile', accounts.editProfile);

    var tournament = require('cloud/tournament/actions');
    app.get('/tournament', tournament.view);

    var dashboard = require('cloud/dashboard/actions')(keys);
    app.get('/dashboard', loginRequired, dashboard.spuds);
    app.get('/dashboard/general', loginRequired, dashboard.general);
    
    app.get('/dashboard/fans/spuds', loginRequired, dashboard.mySpuds);
    app.get('/dashboard/fans/favorites', loginRequired, dashboard.myFavorites);
    app.get('/dashboard/fans/settings', loginRequired, dashboard.settings);
    app.get('/dashboard/fans/basicInfo', loginRequired, dashboard.basicInfo);

    app.get('/dashboard/recipient/:teamID', loginRequired, dashboard.recipient);
    app.get('/dashboard/recipient/:teamID/complete', loginRequired, dashboard.recipient_complete);

    app.get('/dashboard/sponsor', loginRequired, dashboard.sponsor);
    app.post('/dashboard/sponsor/confirm', loginRequired, dashboard.sponsor_confirm);
    app.get('/dashboard/sponsor/complete', loginRequired, dashboard.sponsor_complete);

    app.get('/dashboard/donations', loginRequired, dashboard.list_donations);

    var teams = require('cloud/dashboard/teams/teams')(keys);
    app.get('/dashboard/teams', loginRequired, teams.list.get);
    app.get('/dashboard/teams/create', loginRequired, teams.create.get);
    app.post('/dashboard/teams/create', loginRequired, teams.create.post);
    app.get('/dashboard/teams/edit/:id', loginRequired, teams.edit.get);
    app.post('/dashboard/teams/edit', loginRequired, teams.edit.post);
    app.get('/dashboard/teams/remove/:id', loginRequired, teams.remove.get);

    var teamOffers = require('cloud/dashboard/teams/offers')(keys);
    app.get('/dashboard/teams/:id/offers', loginRequired, teamOffers.list.get);
    app.get('/dashboard/teams/:id/offers/create', loginRequired, teamOffers.create.get);
    app.post('/dashboard/teams/:id/offers/create', loginRequired, teamOffers.create.post);

    var spudmart = require('cloud/spudmart/actions');
    app.get('/spudmart', spudmart.view);
    app.get('/spudmart/offer', spudmart.offer);
};