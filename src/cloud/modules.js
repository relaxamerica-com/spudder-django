module.exports = function (app, keys) {
    var home = require('cloud/home/actions');
    app.get('/', home.home);

    var accounts = require('cloud/accounts/actions')(keys);
    app.post('/accounts/login', accounts.login);
    app.post('/accounts/register', accounts.register);
    app.get('/accounts/logout', accounts.logout);

    var tournament = require('cloud/tournament/actions');
    app.get('/tournament', tournament.view);

    var dashboard = require('cloud/dashboard/actions')(keys);
    app.get('/dashboard', dashboard.spuds);
    app.get('/dashboard/general', dashboard.general);

    app.get('/dashboard/recipient', dashboard.recipient);
    app.post('/dashboard/recipient/save', dashboard.recipient_save);
    app.get('/dashboard/recipient/complete', dashboard.recipient_complete);

    app.get('/dashboard/sponsor', dashboard.sponsor);
    app.post('/dashboard/sponsor/confirm', dashboard.sponsor_confirm);
    app.get('/dashboard/sponsor/complete', dashboard.sponsor_complete);

    app.get('/dashboard/donations', dashboard.list_donations);

    var spudmart = require('cloud/spudmart/actions');
    app.get('/spudmart', spudmart.view);
    app.get('/spudmart/offer', spudmart.offer);
};