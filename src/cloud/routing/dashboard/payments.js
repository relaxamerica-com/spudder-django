module.exports = function (app, keys) {
    var helpers = require('cloud/routing/helpers')();

    var recipient = require('cloud/dashboard/payments/recipients')(keys);
    app.get('/dashboard/payments/recipient/:teamID', helpers.loginRequired, recipient.register);
    app.get('/dashboard/payments/recipient/:teamID/complete', helpers.loginRequired, recipient.register_complete);
    app.get('/dashboard/payments/recipient/:teamID/thanks', helpers.loginRequired, recipient.register_thanks);
    app.get('/dashboard/payments/recipient/:teamID/error', helpers.loginRequired, recipient.register_error);

    var donate = require('cloud/dashboard/payments/donate')(keys);
    app.get('/dashboard/payments/donate/:teamID/:offerID', helpers.loginRequired, donate.register);
    app.get('/dashboard/payments/donate/complete', helpers.loginRequired, donate.register_complete);
    app.get('/dashboard/payments/donate/thanks', helpers.loginRequired, donate.register_thanks);
    app.get('/dashboard/payments/donate/error', helpers.loginRequired, donate.register_error);
};